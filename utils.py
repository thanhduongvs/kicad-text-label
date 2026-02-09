import math
import time
import re
import os
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient 

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

def force_orientation(pts, is_ccw=True):
    if len(pts) < 3: return pts
    try:
        poly = Polygon(pts)
        sign = 1.0 if is_ccw else -1.0
        oriented_poly = orient(poly, sign=sign)
        return list(oriented_poly.exterior.coords)
    except: return pts

def stitch_hole_to_shell(shell, hole):
    if not shell or not hole: return shell
    hole_idx = max(range(len(hole)), key=lambda i: hole[i][1]) 
    hole_pt = hole[hole_idx]
    best_shell_idx = -1; min_x_dist = float('inf'); found_below = False
    for i, s_pt in enumerate(shell[:-1]):
        if s_pt[1] > hole_pt[1]: 
            x_dist = abs(s_pt[0] - hole_pt[0])
            if x_dist < min_x_dist: min_x_dist = x_dist; best_shell_idx = i; found_below = True
    if not found_below:
        min_d = float('inf')
        for i, s_pt in enumerate(shell[:-1]):
            d = dist_sq(s_pt, hole_pt)
            if d < min_d: min_d = d; best_shell_idx = i
    if best_shell_idx == -1: return shell
    new_hole = hole[hole_idx:-1] + hole[:hole_idx] + [hole[hole_idx]]
    return (shell[:best_shell_idx+1] + new_hole + [shell[best_shell_idx]] + shell[best_shell_idx+1:])

def organize_and_stitch(contours):
    if not contours: return []
    valid_contours = [c for c in contours if len(c) >= 3]
    if not valid_contours: return []
    try: polys = [Polygon(c) for c in valid_contours]
    except: return valid_contours
    n = len(polys); hierarchy = {i: [] for i in range(n)}; is_child = [False] * n
    areas = [(i, p.area) for i, p in enumerate(polys)]
    areas.sort(key=lambda x: x[1], reverse=True)
    sorted_indices = [x[0] for x in areas]
    for i in range(len(sorted_indices)):
        parent_idx = sorted_indices[i]
        for j in range(i + 1, len(sorted_indices)):
            child_idx = sorted_indices[j]
            if not is_child[child_idx] and polys[parent_idx].contains(polys[child_idx]):
                hierarchy[parent_idx].append(child_idx); is_child[child_idx] = True
    final_paths = []
    for idx in sorted_indices:
        if is_child[idx]: continue
        current_shell = force_orientation(valid_contours[idx], is_ccw=True)
        for h_idx in hierarchy[idx]:
            hole_pts = force_orientation(valid_contours[h_idx], is_ccw=False)
            current_shell = stitch_hole_to_shell(current_shell, hole_pts)
        final_paths.append(current_shell)
    return final_paths

def classify_contours(contours):
    if not contours: return [], []
    valid_contours = [c for c in contours if len(c) >= 3]
    if not valid_contours: return []
    polys = [Polygon(c) for c in valid_contours]
    n = len(polys); is_inner = [False] * n
    sorted_idx = sorted(range(n), key=lambda i: polys[i].area, reverse=True)
    for i in range(len(sorted_idx)):
        parent_i = sorted_idx[i]
        for j in range(i + 1, len(sorted_idx)):
            child_j = sorted_idx[j]
            if not is_inner[child_j] and polys[parent_i].contains(polys[child_j]):
                is_inner[child_j] = True
    return [valid_contours[i] for i in range(n) if not is_inner[i]], [valid_contours[i] for i in range(n) if is_inner[i]]

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

# --- PARSING & GENERATION ---

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
        # Retrieve Font Object from Tuple (TTFont, Path)
        font_data = font_library.get(current_font_key, font_library.get(default_font_key))
        font_obj = font_data[0] if isinstance(font_data, tuple) else font_data
        segments.append((token, font_obj))
    return segments

def create_missing_glyph(x, y, scale, units):
    w = units * 0.6 * scale; h = units * 0.8 * scale
    return [[(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)]]

def generate_polygons_logic(text, font_library, default_font_key, pad_top, pad_bottom, pad_left, pad_right, align, cap_left, cap_right, line_spacing, border_width, corner_radius, is_negative, no_frame):
    base_height = 10.0 
    if not font_library or default_font_key not in font_library: return []
    
    line_step_y = base_height * line_spacing 
    all_text_raw_contours = []; all_pts_text_solid = []
    lines = text.split('\n')
    line_widths = []; parsed_lines = [] 
    
    # 1. PRE-CALCULATE
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
        line_widths.append(total_w)
    max_width = max(line_widths) if line_widths else 0

    # 2. RENDER
    for line_idx, segments in enumerate(parsed_lines):
        cursor_x = get_start_x(align, line_widths[line_idx], max_width)
        cursor_y = line_idx * line_step_y
        for content, font_obj in segments:
            if not font_obj: continue
            glyph_set = font_obj.getGlyphSet(); cmap = font_obj.getBestCmap()
            hmtx = font_obj['hmtx']; units_per_em = font_obj['head'].unitsPerEm
            hhea = font_obj['hhea']
            font_raw_height = hhea.ascent - hhea.descent
            current_scale = base_height / font_raw_height
            
            for char in content:
                code = ord(char)
                if code not in cmap:
                    missing_contours = create_missing_glyph(0, 0, current_scale, units_per_em)
                    offset_y_box = cursor_y - base_height * 0.8
                    processed_char = []
                    for cnt in missing_contours:
                        scaled = [(p[0] + cursor_x, p[1] + offset_y_box) for p in cnt]
                        processed_char.append(scaled)
                        if not is_negative: all_pts_text_solid.extend(scaled)
                    all_text_raw_contours.extend(processed_char)
                    cursor_x += (units_per_em * 0.7) * current_scale
                    continue

                glyph_name = cmap[code]
                pen = SimplePathPen(glyph_set, steps=10)
                glyph_set[glyph_name].draw(pen)
                
                if pen.contours:
                    processed_char = []
                    for cnt in pen.contours:
                        scaled = [(p[0]*current_scale + cursor_x, -p[1]*current_scale + cursor_y) for p in cnt]
                        cleaned = [scaled[0]]
                        for pt in scaled[1:]:
                            if dist_sq(pt, cleaned[-1]) > 1e-8: cleaned.append(pt)
                        if len(cleaned) > 2:
                            processed_char.append(cleaned)
                            if not is_negative: all_pts_text_solid.extend(cleaned)
                    if not is_negative: all_text_raw_contours.extend(organize_and_stitch(processed_char))
                    else: all_text_raw_contours.extend(processed_char)
                cursor_x += hmtx[glyph_name][0] * current_scale

    if no_frame: return center_polygons_at_origin(all_text_raw_contours)

    # 3. SHELL & CAPS
    pts_for_box = [p for cnt in all_text_raw_contours for p in cnt] if is_negative else all_pts_text_solid
    if not pts_for_box: return []
    min_x = min(p[0] for p in pts_for_box); max_x = max(p[0] for p in pts_for_box)
    min_y = min(p[1] for p in pts_for_box); max_y = max(p[1] for p in pts_for_box)
    current_box_height = (max_y - min_y) + pad_top + pad_bottom
    radius = current_box_height / 2; slant = current_box_height * 0.25 
    
    extra_left = 0; extra_right = 0
    if cap_left == 'Ribbon_In': extra_left = radius
    elif cap_left in ['Trap_Left', 'Trap_Right']: extra_left = slant 
    if cap_right == 'Ribbon_In': extra_right = radius
    elif cap_right in ['Trap_Left', 'Trap_Right']: extra_right = slant

    rect_left = min_x - pad_left - extra_left; rect_right = max_x + pad_right + extra_right
    rect_top = min_y - pad_top; rect_bottom = max_y + pad_bottom
    tl = (rect_left, rect_top); tr = (rect_right, rect_top)
    br = (rect_right, rect_bottom); bl = (rect_left, rect_bottom)

    if cap_left == 'Trap_Left': tl = (rect_left + slant, rect_top); bl = (rect_left - slant, rect_bottom)
    elif cap_left == 'Trap_Right': tl = (rect_left - slant, rect_top); bl = (rect_left + slant, rect_bottom)
    if cap_right == 'Trap_Left': tr = (rect_right + slant, rect_top); br = (rect_right - slant, rect_bottom)
    elif cap_right == 'Trap_Right': tr = (rect_right - slant, rect_top); br = (rect_right + slant, rect_bottom)

    shell_pts = [tl, tr]
    if cap_right not in ['Trap_Left', 'Trap_Right']: shell_pts.extend(create_cap_path(rect_right, rect_top, rect_bottom, cap_right, False))
    shell_pts.extend([br, bl])
    if cap_left not in ['Trap_Left', 'Trap_Right']: shell_pts.extend(create_cap_path(rect_left, rect_top, rect_bottom, cap_left, True))
    shell_pts.append(shell_pts[0])
    
    safe_r = min(corner_radius, current_box_height/2.1)
    shell_pts = apply_corner_radius_to_poly(shell_pts, safe_r)
    
    # 4. BOOLEAN
    if is_negative:
        if not all_text_raw_contours: return []
        text_outers, text_inners = classify_contours(all_text_raw_contours)
        final_bg = force_orientation(shell_pts, is_ccw=True)
        for letter in text_outers:
            hole_letter = force_orientation(letter, is_ccw=False)
            final_bg = stitch_hole_to_shell(final_bg, hole_letter)
        clean_inners = [force_orientation(inner, is_ccw=True) for inner in text_inners]
        return center_polygons_at_origin([final_bg] + clean_inners)
    else:
        outer_poly = Polygon(shell_pts)
        inner_poly = outer_poly.buffer(-border_width, join_style=2) 
        try: frame_poly = outer_poly.difference(inner_poly)
        except: frame_poly = outer_poly 
        frame_contours = []
        def process_shapely_to_path(poly):
            shell = force_orientation(list(poly.exterior.coords), is_ccw=True)
            for interior in poly.interiors:
                hole = force_orientation(list(interior.coords), is_ccw=False)
                shell = stitch_hole_to_shell(shell, hole)
            return shell
        if frame_poly.geom_type == 'Polygon': frame_contours.append(process_shapely_to_path(frame_poly))
        elif frame_poly.geom_type == 'MultiPolygon':
            for p in frame_poly.geoms: frame_contours.append(process_shapely_to_path(p))
        return center_polygons_at_origin(all_text_raw_contours + frame_contours)

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

def apply_corner_radius_to_poly(poly_pts, radius):
    if radius <= 0.01: return poly_pts
    try:
        poly = Polygon(poly_pts)
        return list(poly.buffer(-radius, join_style=1).buffer(2*radius, join_style=1).buffer(-radius, join_style=1).exterior.coords)
    except: return poly_pts

def generate_kicad_sexpr(polys, footprint_name="KiBuzzard_Gen", layer="F.Cu"):
    tedit = hex(int(time.time()))[2:].upper()
    all_pts = [p for poly in polys for p in poly]
    ref_y, val_y = (min(p[1] for p in all_pts)-2, max(p[1] for p in all_pts)+2) if all_pts else (-5, 5)
    s_expr = [f'(footprint "{footprint_name}" (layer "{layer}") (tedit {tedit}) (generator kibuzzard_clone)']
    s_expr.append('  (attr board_only exclude_from_pos_files exclude_from_bom)')
    s_expr.append(f'  (fp_text reference "{footprint_name}" (at 0 {ref_y:.4f}) (layer "F.SilkS") hide (effects (font (size 1 1) (thickness 0.15))))')
    s_expr.append(f'  (fp_text value "G***" (at 0 {val_y:.4f}) (layer "F.SilkS") hide (effects (font (size 1 1) (thickness 0.15))))')
    for poly in polys:
        if len(poly) < 3: continue
        s_expr.append('  (fp_poly (pts'); 
        for x, y in poly: s_expr.append(f'      (xy {x:.6f} {y:.6f})')
        s_expr.append(f'    ) (layer "{layer}") (width 0))')
    s_expr.append(")")
    return "\n".join(s_expr)

def sanitize_font_key(filename):
    name = os.path.splitext(filename)[0]
    # Thay thế ký tự không phải chữ số thành _
    clean_name = re.sub(r'[^a-zA-Z0-9]', '_', name)
    return clean_name