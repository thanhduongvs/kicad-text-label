from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPathItem, QGraphicsLineItem
from PySide6.QtGui import QPainter, QPainterPath, QPen, QColor, QBrush, QPolygonF
from PySide6.QtCore import Qt, QPointF

class PreviewWidget(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setBackgroundBrush(QBrush(QColor("#2c3e50")))
        self.path_item = QGraphicsPathItem()
        self.scene.addItem(self.path_item)
        self.path_item.setPen(QPen(Qt.NoPen))
        pen_origin = QPen(QColor("#e74c3c")) # Màu đỏ
        pen_origin.setWidth(0) # Cosmetic pen (luôn mảnh 1px dù zoom thế nào)
        line_x = QGraphicsLineItem(-1, 0, 1, 0)
        line_y = QGraphicsLineItem(0, -1, 0, 1)
        line_x.setPen(pen_origin)
        line_y.setPen(pen_origin)
        self.scene.addItem(line_x)
        self.scene.addItem(line_y)

    def update_content(self, polys, color="#F5B041"):
        self.path_item.setBrush(QBrush(QColor(color))) 
        qt_path = QPainterPath()
        for poly_pts in polys:
            if len(poly_pts) < 3: continue
            qpoly = QPolygonF()
            for x, y in poly_pts: qpoly.append(QPointF(x, y))
            qt_path.addPolygon(qpoly); qt_path.closeSubpath()
        self.path_item.setPath(qt_path)
        rect = qt_path.boundingRect()
        if not rect.isEmpty():
            self.scene.setSceneRect(rect.adjusted(-20, -20, 20, 20))
            self.fitInView(self.path_item, Qt.KeepAspectRatio)
            self.scale(0.9, 0.9)

    def wheelEvent(self, event):
        factor = 1.15 if event.angleDelta().y() > 0 else 1/1.15
        self.scale(factor, factor)

class PreviewWidget2(QGraphicsView):
    def __init__(self, parent=None):
        """
        Khởi tạo Widget.
        QUAN TRỌNG: Tham số 'parent' là bắt buộc để dùng với Qt Designer (Promoted Widgets).
        """
        super().__init__(parent)
        
        # 1. Setup Scene
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        
        # 2. Setup Render Quality & Interaction
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag) # Cho phép kéo chuột để di chuyển
        self.setBackgroundBrush(QBrush(QColor("#2c3e50"))) # Màu nền tối
        
        # Tắt thanh cuộn để giao diện sạch hơn (tùy chọn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # 3. Main Path Item (Chứa hình dạng chữ)
        self.path_item = QGraphicsPathItem()
        self.path_item.setPen(QPen(Qt.NoPen)) # Không vẽ viền
        self.scene.addItem(self.path_item)

        # 4. Origin Crosshair (Dấu cộng tâm 0,0 - Rất quan trọng khi làm PCB)
        pen_origin = QPen(QColor("#e74c3c")) # Màu đỏ
        pen_origin.setWidth(0) # Cosmetic pen (luôn mảnh 1px dù zoom thế nào)
        line_x = QGraphicsLineItem(-5, 0, 5, 0)
        line_y = QGraphicsLineItem(0, -5, 0, 5)
        line_x.setPen(pen_origin)
        line_y.setPen(pen_origin)
        self.scene.addItem(line_x)
        self.scene.addItem(line_y)

    def update_content(self, polys, color="#F5B041"):
        """Cập nhật nội dung hiển thị từ danh sách polygons."""
        # 1. Clear cũ hoặc xử lý rỗng
        if not polys:
            self.path_item.setPath(QPainterPath())
            return

        # 2. Update Color
        self.path_item.setBrush(QBrush(QColor(color))) 
        
        # 3. Build Path
        qt_path = QPainterPath()
        for poly_pts in polys:
            if len(poly_pts) < 3: 
                continue
            
            qpoly = QPolygonF()
            for x, y in poly_pts: 
                qpoly.append(QPointF(x, y))
            
            qt_path.addPolygon(qpoly)
            qt_path.closeSubpath() # Đóng polygon để tô màu đúng
            
        self.path_item.setPath(qt_path)
        
        # 4. Auto Zoom/Fit (Chỉ zoom khi nội dung thay đổi đáng kể hoặc lần đầu)
        rect = qt_path.boundingRect()
        if not rect.isEmpty():
            # Reset transform cũ để tránh zoom chồng chéo
            # self.resetTransform() 
            
            # Thêm lề (padding) 20px xung quanh để nhìn thoáng hơn
            self.scene.setSceneRect(rect.adjusted(-20, -20, 20, 20))
            self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
            self.scale(0.9, 0.9) # Thu nhỏ lại 90% để không sát viền

    def wheelEvent(self, event):
        """Xử lý Zoom bằng chuột."""
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor

        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor

        self.scale(zoom_factor, zoom_factor)