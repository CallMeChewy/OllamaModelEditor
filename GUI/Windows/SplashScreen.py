# File: SplashScreen.py
# Path: OllamaModelEditor/GUI/Windows/SplashScreen.py
# Standard: AIDEV-PascalCase-1.2
# Created: 2025-03-11
# Last Modified: 2025-03-11
# Description: Splash screen for the OllamaModelEditor application

from PySide6.QtWidgets import QSplashScreen, QVBoxLayout, QLabel, QProgressBar, QWidget
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QPixmap, QFont, QColor, QPainter

class SplashScreen(QSplashScreen):
    """Splash screen displayed during application startup."""
    
    def __init__(self):
        """Initialize the splash screen."""
        # Create a pixmap for the splash screen
        Pixmap = QPixmap(QSize(600, 400))
        Pixmap.fill(Qt.white)
        
        super().__init__(Pixmap)
        
        # Create a painter to draw on the pixmap
        Painter = QPainter(self.pixmap())
        self._DrawContent(Painter)
        Painter.end()
        
        # Set window flags
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        
        # Initialize progress
        self.Progress = 0
        self.ProgressMax = 100
        
        # Start progress timer
        self.ProgressTimer = QTimer(self)
        self.ProgressTimer.timeout.connect(self._UpdateProgress)
        self.ProgressTimer.start(30)
    
    def _DrawContent(self, Painter):
        """
        Draw splash screen content.
        
        Args:
            Painter: QPainter instance to draw with
        """
        # Draw application name
        Painter.setPen(QColor(40, 40, 40))
        TitleFont = QFont("Arial", 28, QFont.Bold)
        Painter.setFont(TitleFont)
        Painter.drawText(50, 100, "Ollama Model Editor")
        
        # Draw tagline
        TaglineFont = QFont("Arial", 14)
        Painter.setFont(TaglineFont)
        Painter.drawText(50, 140, "A powerful tool for customizing and optimizing Ollama AI models")
        
        # Draw version
        VersionFont = QFont("Arial", 10)
        Painter.setFont(VersionFont)
        Painter.drawText(50, 180, "Version 1.0.0")
        
        # Draw credits
        CreditsFont = QFont("Arial", 10)
        Painter.setFont(CreditsFont)
        Painter.setPen(QColor(100, 100, 100))
        Painter.drawText(50, 350, "© 2025 Herbert J. Bowers")
        Painter.drawText(50, 370, "A Human-AI Collaboration Project")
        
        # Draw progress bar frame
        Painter.setPen(QColor(200, 200, 200))
        Painter.setBrush(Qt.white)
        Painter.drawRect(50, 250, 500, 30)
    
    def _UpdateProgress(self):
        """Update progress bar display."""
        if self.Progress >= self.ProgressMax:
            self.ProgressTimer.stop()
            return
        
        # Increase progress
        self.Progress += 2
        
        # Update progress bar
        Painter = QPainter(self.pixmap())
        Painter.setPen(Qt.NoPen)
        Painter.setBrush(QColor(0, 120, 212))
        
        # Calculate progress width
        ProgressWidth = int(500 * (self.Progress / self.ProgressMax))
        Painter.drawRect(50, 250, ProgressWidth, 30)
        
        # Draw status text
        Painter.setPen(QColor(40, 40, 40))
        StatusFont = QFont("Arial", 10)
        Painter.setFont(StatusFont)
        
        # Determine status message based on progress
        StatusMessage = "Initializing..."
        if self.Progress > 20:
            StatusMessage = "Loading configuration..."
        if self.Progress > 40:
            StatusMessage = "Connecting to Ollama API..."
        if self.Progress > 60:
            StatusMessage = "Loading model information..."
        if self.Progress > 80:
            StatusMessage = "Preparing UI components..."
        
        Painter.drawText(50, 220, StatusMessage)
        Painter.end()
        
        # Update display
        self.repaint()
    
    def mousePressEvent(self, event):
        """
        Handle mouse press events.
        
        Mouse clicks will hide the splash screen.
        
        Args:
            event: Mouse event
        """
        self.hide()
