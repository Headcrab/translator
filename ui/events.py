from PyQt5.QtCore import QEvent

class UpdateTranslationEvent(QEvent):
    _type = QEvent.Type(QEvent.registerEventType())
    
    def __init__(self, text):
        super().__init__(self._type)
        self.text = text

# Удаляем неиспользуемый метакласс
# class StreamHandlerMeta(pyqtWrapperType, type(QEvent)):
#     pass 