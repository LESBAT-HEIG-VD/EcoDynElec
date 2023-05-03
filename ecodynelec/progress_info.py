import ipywidgets as widgets
from IPython.core.display_functions import display


class ProgressInfo:
    def __init__(self, label: str = 'not set', max: int = 10, color: str = None, width: str = '80%') -> None:
        super().__init__()
        self.l0label = label
        self.label = widgets.Label(value=label)
        self.bar = widgets.IntProgress(min=0, max=max)
        self.bar.layout.width = width
        if color:
            self.bar.style.bar_color = color
        self.vbox = widgets.VBox([self.label, self.bar])
        display(self.vbox)

    def set_max_value(self, max: int):
        self.bar.max = max
        self.set_progress(0)

    def progress(self, label: str = None, amount: int = 1):
        if label is not None:
            self.reset_sub_label()
            self.l0label = label
            self.label.value = label
        self.bar.value += amount

    def set_progress(self, progress: int):
        self.bar.value = progress

    def set_sub_label(self, label: str):
        self.label.value = self.l0label + ' - ' + label

    def reset_sub_label(self):
        self.label.value = self.l0label

    def hide(self):
        self.vbox.layout.display = 'none'

    def show(self):
        self.vbox.layout.display = 'block'
