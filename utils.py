import math
import time
import re
import os
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from shapely.geometry import Polygon
from shapely.validation import make_valid

from PySide6.QtGui import QImage, QPainter, QPainterPath, QColor, QBrush, QPen, QTransform
from PySide6.QtCore import Qt, QPointF

# --- CÁC HÀM HELPER CƠ BẢN (KHÔNG ĐỔI) ---

class SimplePathPen(BasePen):
    def __init__(self, glyphSet, steps=12):
        super().__init__(glyphSet)
        self.steps = steps
        self.contours = []
        self.current_contour = []
    def _moveTo(self, pt):
        if self.current_contour: self.contours.append(self.current_contour)
        self.current_contour = [pt]
    def _lineTo(self, pt): self.current_contour.append(pt)
    def _qCurveToOne(self, p1, p2):
        start = self.current_contour[-1]
        for i in range(1, self.steps + 1):
            t = i / self.steps
            x = (1-t)**2 * start[0] + 2*(1-t)*t * p1[0] + t**2 * p2[0]
            y = (1-t)**2 * start[1] + 2*(1-t)*t * p1[1] + t**2 * p2[1]
            self.current_contour.append((x, y))
    def _curveToOne(self, p1, p2, p3):
        start = self.current_contour[-1]
        for i in range(1, self.steps + 1):
            t = i / self.steps
            x = (1-t)**3*start[0] + 3*(1-t)**2*t*p1[0] + 3*(1-t)*t**2*p2[0] + t**3*p3[0]
            y = (1-t)**3*start[1] + 3*(1-t)**2*t*p1[1] + 3*(1-t)*t**2*p2[1] + t**3*p3[1]
            self.current_contour.append((x, y))
    def _closePath(self):
        if self.current_contour:
            if self.current_contour[0] != self.current_contour[-1]:
                self.current_contour.append(self.current_contour[0])
            self.contours.append(self.current_contour)
            self.current_contour = []

def dist_sq(p1, p2): return (p1[0]-p2[0])**2 + (p1[1]-p2[1])**2

def get_start_x(align, line_width, max_width):
    if align == 'Center': return (max_width - line_width) / 2
    elif align == 'Right': return max_width - line_width
    return 0

def create_cap_path(x, y_min, y_max, cap_type, is_left, steps=30):
    points = []
    height = y_max - y_min; radius = height / 2; center_y = (y_min + y_max) / 2
    if cap_type == 'Square': return [] 
    elif cap_type == 'Triangle': points.append((x + (-radius if is_left else radius), center_y))
    elif cap_type == 'Pointed': points.append((x + (-height if is_left else height), center_y))
    elif cap_type == 'Ribbon_Out': points.append((x + (-radius if is_left else radius), center_y))
    elif cap_type == 'Ribbon_In': points.append((x + (radius if is_left else -radius), center_y))
    elif cap_type == 'Round':
        steps = 32 
        start, end = (math.pi/2, 3*math.pi/2) if is_left else (-math.pi/2, math.pi/2)
        for i in range(steps):
            t = start + (end - start) * (i + 1) / (steps + 1)
            points.append((x + radius * math.cos(t), center_y + radius * math.sin(t)))
    return points

def parse_rich_text(text_line, font_library, default_font_key='default'):
    tokens = re.split(r'(\{[a-zA-Z0-9_]+\}|\{\/[a-zA-Z0-9_]+\})', text_line)
    segments = []
    current_font_key = default_font_key
    font_stack = [default_font_key]
    for token in tokens:
        if not token: continue
        if token.startswith('{/') and token.endswith('}'):
            if len(font_stack) > 1: font_stack.pop(); current_font_key = font_stack[-1]
            continue
        if token.startswith('{') and token.endswith('}'):
            tag = token[1:-1]
            if tag in font_library: current_font_key = tag; font_stack.append(tag)
            continue
        font_data = font_library.get(current_font_key, font_library.get(default_font_key))
        font_obj = font_data[0] if isinstance(font_data, tuple) else font_data
        segments.append((token, font_obj))
    return segments

def create_missing_glyph(x, y, scale, units):
    w = units * 0.6 * scale; h = units * 0.8 * scale
    return [[(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)]]

def sanitize_font_key(filename):
    name = os.path.splitext(filename)[0]
    clean_name = re.sub(r'[^a-zA-Z0-9]', '_', name)
    return clean_name

# --- RASTERIZATION & UTILS ---

def raster_to_polygons(painter_path, resolution=40.0):
    rect = painter_path.boundingRect()
    if rect.isEmpty(): return []
    margin = 2.0 
    x_min, y_min = rect.x() - margin, rect.y() - margin
    width_mm = rect.width() + 2 * margin
    height_mm = rect.height() + 2 * margin
    img_w = int(math.ceil(width_mm * resolution))
    img_h = int(math.ceil(height_mm * resolution))
    if img_w <= 0 or img_h <= 0: return []

    image = QImage(img_w, img_h, QImage.Format_RGB32)
    image.fill(Qt.black) 
    painter = QPainter(image)
    painter.setRenderHint(QPainter.Antialiasing, False) 
    painter.scale(resolution, resolution)
    painter.translate(-x_min, -y_min)
    painter.setPen(Qt.NoPen); painter.setBrush(QColor(255, 255, 255)) 
    try: painter.drawPath(painter_path)
    finally: painter.end() 
    
    rects = []
    px_size = 1.0 / resolution
    for y in range(img_h):
        start_x = -1
        for x in range(img_w):
            if (image.pixel(x, y) & 0x00FFFFFF) != 0: 
                if start_x == -1: start_x = x
            else:
                if start_x != -1:
                    rect_w = (x - start_x) * px_size
                    rect_h = px_size
                    real_x = x_min + (start_x * px_size)
                    real_y = y_min + (y * px_size)
                    rects.append([(real_x, real_y), (real_x + rect_w, real_y), (real_x + rect_w, real_y + rect_h), (real_x, real_y + rect_h), (real_x, real_y)])
                    start_x = -1
        if start_x != -1:
            rect_w = (img_w - start_x) * px_size
            rect_h = px_size
            real_x = x_min + (start_x * px_size)
            real_y = y_min + (y * px_size)
            rects.append([(real_x, real_y), (real_x + rect_w, real_y), (real_x + rect_w, real_y + rect_h), (real_x, real_y + rect_h), (real_x, real_y)])
    return rects

def center_polygons_at_origin(polys):
    if not polys: return []
    all_pts = [p for poly in polys for p in poly]
    if not all_pts: return polys
    min_x = min(p[0] for p in all_pts); max_x = max(p[0] for p in all_pts)
    min_y = min(p[1] for p in all_pts); max_y = max(p[1] for p in all_pts)
    center_x = (min_x + max_x) / 2; center_y = (min_y + max_y) / 2
    return [[(p[0] - center_x, p[1] - center_y) for p in poly] for poly in polys]

def scale_polys_to_target_height(polys, target_height_mm):
    if not polys: return []
    all_pts = [p for poly in polys for p in poly]
    if not all_pts: return polys
    min_y = min(p[1] for p in all_pts); max_y = max(p[1] for p in all_pts)
    current_height = max_y - min_y
    if current_height < 1e-6: return polys 
    scale_factor = target_height_mm / current_height
    return [[(p[0] * scale_factor, p[1] * scale_factor) for p in poly] for poly in polys]

def apply_anchor_point(polys, anchor_mode):
    if not polys: return []
    all_pts = [p for poly in polys for p in poly]
    if not all_pts: return polys
    min_x = min(p[0] for p in all_pts); max_x = max(p[0] for p in all_pts)
    min_y = min(p[1] for p in all_pts); max_y = max(p[1] for p in all_pts)
    center_x = (min_x + max_x) / 2; center_y = (min_y + max_y) / 2
    dx = 0; dy = 0
    if anchor_mode == "Center-Center": dx, dy = -center_x, -center_y
    elif anchor_mode == "Top-Left": dx, dy = -min_x, -min_y
    elif anchor_mode == "Top-Center": dx, dy = -center_x, -min_y
    elif anchor_mode == "Top-Right": dx, dy = -max_x, -min_y
    elif anchor_mode == "Center-Left": dx, dy = -min_x, -center_y
    elif anchor_mode == "Center-Right": dx, dy = -max_x, -center_y
    elif anchor_mode == "Bottom-Left": dx, dy = -min_x, -max_y
    elif anchor_mode == "Bottom-Center": dx, dy = -center_x, -max_y
    elif anchor_mode == "Bottom-Right": dx, dy = -max_x, -max_y
    return [[(p[0] + dx, p[1] + dy) for p in poly] for poly in polys]

def generate_kicad_sexpr(polys, footprint_name="KiBuzzard_Gen", layer="F.Cu"):
    tedit = hex(int(time.time()))[2:].upper()
    all_pts = [p for poly in polys for p in poly]
    ref_y, val_y = (-5, 5)
    if all_pts:
        min_y = min(p[1] for p in all_pts)
        max_y = max(p[1] for p in all_pts)
        ref_y = min_y - 1.5
        val_y = max_y + 1.5

    s_expr = [f'(footprint "{footprint_name}" (layer "{layer}") (tedit {tedit}) (generator kibuzzard_clone)']
    s_expr.append('  (attr board_only exclude_from_pos_files exclude_from_bom)')
    s_expr.append(f'  (fp_text reference "{footprint_name}" (at 0 {ref_y:.4f}) (layer "F.SilkS") hide (effects (font (size 1 1) (thickness 0.15))))')
    s_expr.append(f'  (fp_text value "G***" (at 0 {val_y:.4f}) (layer "F.SilkS") hide (effects (font (size 1 1) (thickness 0.15))))')
    
    for poly in polys:
        if len(poly) < 3: continue
        s_expr.append('  (fp_poly (pts'); 
        for x, y in poly: s_expr.append(f'      (xy {x:.4f} {y:.4f})')
        s_expr.append(f'    ) (layer "{layer}") (width 0))') 
    s_expr.append(")")
    return "\n".join(s_expr)

# --- LOGIC VẼ CHÍNH ---

def generate_polygons_logic(text, font_library, default_font_key, pad_top, pad_bottom, pad_left, pad_right, align, cap_left, cap_right, line_spacing, border_width, corner_radius, is_negative, no_frame, 
                            is_circular=False, radius=20.0, start_angle=0.0, is_fit_angle=False, total_angle=180.0):
    base_height = 10.0 
    if not font_library or default_font_key not in font_library: return []
    
    lines = text.split('\n')
    if is_circular:
        lines = [" ".join(lines)] 

    line_widths = []; parsed_lines = [] 
    
    for line in lines:
        segments = parse_rich_text(line, font_library, default_font_key)
        parsed_lines.append(segments)
        total_w = 0
        for content, font_obj in segments:
            if not font_obj: continue
            head = font_obj['head']; hhea = font_obj['hhea']
            f_height = hhea.ascent - hhea.descent
            scale = base_height / f_height
            cmap = font_obj.getBestCmap(); hmtx = font_obj['hmtx']
            for char in content:
                code = ord(char)
                if code in cmap: total_w += hmtx[cmap[code]][0] * scale
                else: total_w += (head.unitsPerEm * 0.7) * scale
        
        extra_space = 0
        if is_circular and line_spacing > 1.0:
            extra_space = (line_spacing - 1.0) * (base_height * 0.5) * len(line)
        line_widths.append(total_w + extra_space)
        
    max_width = max(line_widths) if line_widths else 0

    text_path = QPainterPath()
    text_path.setFillRule(Qt.WindingFill)
    
    if is_circular:
        # --- CHẾ ĐỘ TRÒN (RADIUS = OUTER RADIUS) ---
        width_stretch_factor = 1.0
        
        if is_fit_angle and total_angle > 0.1 and max_width > 0:
            natural_angle_span = (max_width / radius) * (180.0 / math.pi)
            if natural_angle_span > 0: width_stretch_factor = total_angle / natural_angle_span
        elif not is_fit_angle:
            circumference = 2 * math.pi * radius
            if max_width > circumference:
                shrink = circumference / max_width
                width_stretch_factor = shrink * 0.99 
        
        current_angle = start_angle
        actual_arc_len = max_width * width_stretch_factor
        
        if align == 'Center':
             total_angle_deg = (actual_arc_len / radius) * (180.0 / math.pi)
             current_angle -= total_angle_deg / 2
        elif align == 'Right':
             total_angle_deg = (actual_arc_len / radius) * (180.0 / math.pi)
             current_angle -= total_angle_deg

        spacing_add_mm = 0
        if line_spacing > 1.0: spacing_add_mm = (line_spacing - 1.0) * (base_height * 0.5)

        for segments in parsed_lines:
            for content, font_obj in segments:
                if not font_obj: continue
                glyph_set = font_obj.getGlyphSet(); cmap = font_obj.getBestCmap()
                hmtx = font_obj['hmtx']; units_per_em = font_obj['head'].unitsPerEm
                hhea = font_obj['hhea']
                f_height = hhea.ascent - hhea.descent
                
                scale_y = base_height / f_height
                scale_x = scale_y * width_stretch_factor
                
                # [QUAN TRỌNG] Tính Ascent theo scale mới để canh Outer Radius
                scaled_ascent = hhea.ascent * scale_y
                
                current_spacing = spacing_add_mm * width_stretch_factor

                for char in content:
                    code = ord(char)
                    char_width_natural = 0 
                    raw_char_path = QPainterPath()
                    
                    if code not in cmap:
                        missing_contours = create_missing_glyph(0, 0, scale_y, units_per_em)
                        for cnt in missing_contours:
                            sub_path = QPainterPath()
                            if cnt:
                                sub_path.moveTo(cnt[0][0], cnt[0][1])
                                for pt in cnt[1:]: sub_path.lineTo(pt[0], pt[1])
                                sub_path.closeSubpath()
                            raw_char_path.addPath(sub_path)
                        char_width_natural = (units_per_em * 0.7) * scale_y
                    else:
                        glyph_name = cmap[code]
                        pen = SimplePathPen(glyph_set, steps=10)
                        glyph_set[glyph_name].draw(pen)
                        if pen.contours:
                            for cnt in pen.contours:
                                if len(cnt) < 2: continue
                                start_pt = (cnt[0][0]*scale_x, -cnt[0][1]*scale_y)
                                raw_char_path.moveTo(*start_pt)
                                for pt in cnt[1:]:
                                    next_pt = (pt[0]*scale_x, -pt[1]*scale_y)
                                    raw_char_path.lineTo(*next_pt)
                                raw_char_path.closeSubpath()
                        char_width_natural = hmtx[glyph_name][0] * scale_y
                    
                    char_width_final = char_width_natural * width_stretch_factor
                    total_char_occupy = char_width_final + current_spacing
                    char_angle_span = (total_char_occupy / radius) * (180.0 / math.pi)
                    center_char_angle = current_angle + (char_angle_span / 2)
                    
                    t = QTransform()
                    t.rotate(center_char_angle + 90) 
                    
                    # [QUAN TRỌNG] Dịch chuyển để đỉnh chữ chạm Radius
                    # -radius: đưa baseline ra mép ngoài
                    # +scaled_ascent: lùi baseline về tâm một đoạn = chiều cao ascent
                    # => Đỉnh (Ascent) sẽ nằm đúng tại -radius
                    t.translate(0, -radius + scaled_ascent) 
                    
                    t.translate(-char_width_final / 2, 0)
                    text_path.addPath(t.map(raw_char_path))
                    current_angle += char_angle_span
        final_path = text_path

    else:
        # --- LINEAR MODE ---
        line_step_y = base_height * line_spacing 
        for line_idx, segments in enumerate(parsed_lines):
            cursor_x = get_start_x(align, line_widths[line_idx], max_width)
            cursor_y = line_idx * line_step_y
            
            for content, font_obj in segments:
                if not font_obj: continue
                glyph_set = font_obj.getGlyphSet(); cmap = font_obj.getBestCmap()
                hmtx = font_obj['hmtx']; units_per_em = font_obj['head'].unitsPerEm
                hhea = font_obj['hhea']
                f_height = hhea.ascent - hhea.descent
                current_scale = base_height / f_height
                
                for char in content:
                    code = ord(char)
                    if code not in cmap:
                        missing_contours = create_missing_glyph(0, 0, current_scale, units_per_em)
                        for cnt in missing_contours:
                            sub_path = QPainterPath()
                            offset_y_box = cursor_y - base_height * 0.8
                            if cnt:
                                sub_path.moveTo(cnt[0][0] + cursor_x, cnt[0][1] + offset_y_box)
                                for pt in cnt[1:]: sub_path.lineTo(pt[0] + cursor_x, pt[1] + offset_y_box)
                                sub_path.closeSubpath()
                            text_path.addPath(sub_path)
                        cursor_x += (units_per_em * 0.7) * current_scale
                        continue

                    glyph_name = cmap[code]
                    pen = SimplePathPen(glyph_set, steps=10)
                    glyph_set[glyph_name].draw(pen)
                    
                    if pen.contours:
                        char_path = QPainterPath()
                        for cnt in pen.contours:
                            if len(cnt) < 2: continue
                            start_pt = (cnt[0][0]*current_scale + cursor_x, -cnt[0][1]*current_scale + cursor_y)
                            char_path.moveTo(*start_pt)
                            for pt in cnt[1:]:
                                next_pt = (pt[0]*current_scale + cursor_x, -pt[1]*current_scale + cursor_y)
                                char_path.lineTo(*next_pt)
                            char_path.closeSubpath()
                        text_path.addPath(char_path)
                    cursor_x += hmtx[glyph_name][0] * current_scale

        final_path = QPainterPath()
        if no_frame: final_path = text_path
        else:
            brect = text_path.boundingRect()
            if brect.isEmpty(): brect = QPointF(0,0); min_x=0; max_x=0; min_y=0; max_y=0
            else: min_x = brect.x(); max_x = min_x + brect.width(); min_y = brect.y(); max_y = min_y + brect.height()

            rect_left = min_x - pad_left; rect_right = max_x + pad_right
            rect_top = min_y - pad_top; rect_bottom = max_y + pad_bottom
            current_box_height = (rect_bottom - rect_top)
            radius_frame = current_box_height / 2; slant = current_box_height * 0.25 
            extra_left = 0; extra_right = 0
            
            if cap_left == 'Ribbon_In': extra_left = radius_frame
            elif cap_left in ['Trap_Left', 'Trap_Right']: extra_left = slant 
            if cap_right == 'Ribbon_In': extra_right = radius_frame
            elif cap_right in ['Trap_Left', 'Trap_Right']: extra_right = slant

            final_rect_left = rect_left - extra_left; final_rect_right = rect_right + extra_right
            tl = (final_rect_left, rect_top); tr = (final_rect_right, rect_top)
            br = (final_rect_right, rect_bottom); bl = (final_rect_left, rect_bottom)

            if cap_left == 'Trap_Left': tl = (final_rect_left + slant, rect_top); bl = (final_rect_left - slant, rect_bottom)
            elif cap_left == 'Trap_Right': tl = (final_rect_left - slant, rect_top); bl = (final_rect_left + slant, rect_bottom)
            if cap_right == 'Trap_Left': tr = (final_rect_right + slant, rect_top); br = (final_rect_right - slant, rect_bottom)
            elif cap_right == 'Trap_Right': tr = (final_rect_right - slant, rect_top); br = (final_rect_right + slant, rect_bottom)

            shell_pts = [tl, tr]
            if cap_right not in ['Trap_Left', 'Trap_Right']: 
                shell_pts.extend(create_cap_path(final_rect_right, rect_top, rect_bottom, cap_right, False))
            shell_pts.extend([br, bl])
            if cap_left not in ['Trap_Left', 'Trap_Right']: 
                shell_pts.extend(create_cap_path(final_rect_left, rect_top, rect_bottom, cap_left, True))
            shell_pts.append(shell_pts[0])

            safe_r = min(corner_radius, current_box_height/2.1)
            if safe_r > 0.01:
                try:
                    poly = Polygon(shell_pts)
                    buffered = poly.buffer(-safe_r, join_style=1).buffer(2*safe_r, join_style=1).buffer(-safe_r, join_style=1)
                    shell_pts = list(buffered.exterior.coords)
                except: pass
                
            frame_path = QPainterPath()
            if shell_pts:
                frame_path.moveTo(*shell_pts[0])
                for pt in shell_pts[1:]: frame_path.lineTo(*pt)
                frame_path.closeSubpath()
                
            if is_negative: final_path = frame_path.subtracted(text_path)
            else:
                outer_poly = Polygon(shell_pts)
                inner_poly = outer_poly.buffer(-border_width, join_style=2)
                
                outer_path = QPainterPath()
                outer_pts = list(outer_poly.exterior.coords)
                outer_path.moveTo(*outer_pts[0])
                for pt in outer_pts[1:]: outer_path.lineTo(*pt)
                outer_path.closeSubpath()

                inner_path = QPainterPath()
                inner_pts = list(inner_poly.exterior.coords)
                inner_path.moveTo(*inner_pts[0])
                for pt in inner_pts[1:]: inner_path.lineTo(*pt)
                inner_path.closeSubpath()
                
                frame_border_path = outer_path.subtracted(inner_path)
                final_path = frame_border_path.united(text_path)

    final_polys = raster_to_polygons(final_path, resolution=40.0)
    return center_polygons_at_origin(final_polys)