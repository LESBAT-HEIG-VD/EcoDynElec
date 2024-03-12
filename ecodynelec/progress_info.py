"""A simple labelled progress bar for Jupyter notebooks
"""

import ipywidgets as widgets
from IPython.core.display_functions import display


class ProgressInfo:
    def __init__(self, label: str = 'not set', max: int = 10, color: str = None, width: str = '80%') -> None:
        """Displays a progress bar with the given title

        Parameters
        ----------
        label: str, default to 'not set'
            The text displayed above the progress bar
        max: int, default to 10
            The maximum value of the progress bar
        color: str, default to None
            The color of the progress bar. If None, the default color of IPython is used.
        width: str, default to '80%'
            The width of the progress bar (in pixels or percent of the notebook output width)
        """
        super().__init__()
        self.main_label = label
        self.label = widgets.Label(value=label)
        self.bar = widgets.IntProgress(min=0, max=max)
        self.bar.layout.width = width
        if color:
            self.bar.style.bar_color = color
        self.vbox = widgets.VBox([self.label, self.bar])
        display(self.vbox)

    def set_max_value(self, max: int):
        """Sets the maximum value of the progress bar"""
        self.bar.max = max
        self.set_progress(0)

    def progress(self, label: str = None, amount: int = 1):
        """Increments the progress bar by the given amount and optionally changes the label.
        If the label is changed, the sub label is removed."""
        if label is not None:
            self.reset_sub_label()
            self.main_label = label
            self.label.value = label
        self.bar.value += amount

    def set_progress(self, progress: int):
        """Sets the progress bar to the given value"""
        self.bar.value = progress

    def set_sub_label(self, label: str):
        """Sets the sub label of the progress bar.
        The sub label is displayed as 'main label - sub label'"""
        self.label.value = self.main_label + ' - ' + label

    def reset_sub_label(self):
        """Removes the sub label"""
        self.label.value = self.main_label

    def hide(self):
        """Hides the progress bar"""
        self.vbox.layout.display = 'none'

    def show(self):
        """Shows the progress bar"""
        self.vbox.layout.display = 'block'
