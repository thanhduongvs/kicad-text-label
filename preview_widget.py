from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPathItem, QGraphicsLineItem
from PySide6.QtGui import QPainter, QPainterPath, QPen, QColor, QBrush, QPolygonF
from PySide6.QtCore import Qt, QPointF

class PreviewWidget(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent) # Thêm parent để tương thích tốt hơn với Qt Designer
        
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setBackgroundBrush(QBrush(QColor("#2c3e50")))
        
        # Tắt thanh cuộn để giao diện sạch hơn (vì ta luôn auto-fit)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.path_item = QGraphicsPathItem()
        self.scene.addItem(self.path_item)
        self.path_item.setPen(QPen(Qt.NoPen))
        
        # Crosshair (Tâm 0,0)
        pen_origin = QPen(QColor("#e74c3c")) 
        pen_origin.setWidth(0)
        line_x = QGraphicsLineItem(-1, 0, 1, 0) # Kéo dài ra một chút (-5 đến 5) cho dễ nhìn
        line_y = QGraphicsLineItem(0, -1, 0, 1)
        line_x.setPen(pen_origin)
        line_y.setPen(pen_origin)
        self.scene.addItem(line_x)
        self.scene.addItem(line_y)

    def update_content(self, polys, color="#F5B041"):
        self.path_item.setBrush(QBrush(QColor(color))) 
        
        qt_path = QPainterPath()
        
        # [QUAN TRỌNG] Dòng này sửa lỗi hiển thị font Roboto:
        # Qt.WindingFill giúp tô màu đúng các vùng giao nhau của glyphs
        qt_path.setFillRule(Qt.WindingFill) 

        for poly_pts in polys:
            if len(poly_pts) < 3: continue
            qpoly = QPolygonF()
            for x, y in poly_pts: 
                qpoly.append(QPointF(x, y))
            qt_path.addPolygon(qpoly)
            qt_path.closeSubpath() # Đóng path để tô màu chuẩn
            
        self.path_item.setPath(qt_path)
        
        # --- LOGIC AUTO ZOOM (Giữ nguyên từ code của bạn) ---
        rect = qt_path.boundingRect()
        if not rect.isEmpty():
            # Cập nhật SceneRect để scroll hoạt động đúng vùng
            self.scene.setSceneRect(rect.adjusted(-20, -20, 20, 20))
            
            # Zoom vừa khít với item (path chữ)
            self.fitInView(self.path_item, Qt.KeepAspectRatio)
            
            # Thu nhỏ lại 90% để tạo lề thoáng mắt
            self.scale(0.9, 0.9)

    def resizeEvent(self, event):
        """
        Thêm sự kiện này để khi bạn kéo giãn cửa sổ phần mềm,
        hình ảnh cũng tự động zoom to theo (giữ nguyên logic Auto-fit)
        """
        super().resizeEvent(event)
        if self.path_item.path().elementCount() > 0:
             self.fitInView(self.path_item, Qt.KeepAspectRatio)
             self.scale(0.9, 0.9)

    def wheelEvent(self, event):
        # Giữ nguyên logic zoom chuột của bạn
        factor = 1.15 if event.angleDelta().y() > 0 else 1/1.15
        self.scale(factor, factor)
