from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPathItem, QGraphicsLineItem
from PySide6.QtGui import QPainter, QPainterPath, QPen, QColor, QBrush, QPolygonF
from PySide6.QtCore import Qt, QPointF

class PreviewWidget(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent) # Add parent for better compatibility with Qt Designer
        
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setBackgroundBrush(QBrush(QColor("#2c3e50")))
        
        # Disable scrollbars for a cleaner interface (since we always auto-fit)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.path_item = QGraphicsPathItem()
        self.scene.addItem(self.path_item)
        self.path_item.setPen(QPen(Qt.NoPen))
        
        # Crosshair (Center 0,0)
        pen_origin = QPen(QColor("#e74c3c")) 
        pen_origin.setWidth(0)
        line_x = QGraphicsLineItem(-1, 0, 1, 0) # Extend slightly (-5 to 5) for better visibility
        line_y = QGraphicsLineItem(0, -1, 0, 1)
        line_x.setPen(pen_origin)
        line_y.setPen(pen_origin)
        self.scene.addItem(line_x)
        self.scene.addItem(line_y)

    def update_content(self, polys, color="#F5B041"):
        self.path_item.setBrush(QBrush(QColor(color))) 
        
        qt_path = QPainterPath()
        
        # [IMPORTANT] This line fixes display issues with Roboto font:
        # Qt.WindingFill helps correctly fill intersecting areas of glyphs
        qt_path.setFillRule(Qt.WindingFill) 

        for poly_pts in polys:
            if len(poly_pts) < 3: continue
            qpoly = QPolygonF()
            for x, y in poly_pts: 
                qpoly.append(QPointF(x, y))
            qt_path.addPolygon(qpoly)
            qt_path.closeSubpath() # Close path for accurate filling
            
        self.path_item.setPath(qt_path)
        
        # --- AUTO ZOOM LOGIC (Kept from your code) ---
        rect = qt_path.boundingRect()
        if not rect.isEmpty():
            # Update SceneRect so scrolling works in the correct area
            self.scene.setSceneRect(rect.adjusted(-20, -20, 20, 20))
            
            # Zoom to fit the item (text path)
            self.fitInView(self.path_item, Qt.KeepAspectRatio)
            
            # Scale down to 90% to create visual margins
            self.scale(0.9, 0.9)

    def resizeEvent(self, event):
        """
        Add this event so that when the window is resized,
        the image automatically zooms to fit (keeping the Auto-fit logic)
        """
        super().resizeEvent(event)
        if self.path_item.path().elementCount() > 0:
             self.fitInView(self.path_item, Qt.KeepAspectRatio)
             self.scale(0.9, 0.9)

    def wheelEvent(self, event):
        # Keep your mouse zoom logic
        factor = 1.15 if event.angleDelta().y() > 0 else 1/1.15
        self.scale(factor, factor)
