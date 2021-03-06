import re
import time
import tkinter as tk
import typing as t


class FigureInfo(t.NamedTuple):
    figure_type: str
    # Two points coordinates:
    # The left and the right corner
    coords: t.List[float]
    border_size: float
    border_color: str
    fill_color: str


def figure_from_text(line: str) -> FigureInfo:
    line = line.strip()
    figure_regex = re.compile(".*oval[\s]+(<.*>)"
                              "[\s]+([0-9]+[.]*[0-9]*)[\s]+"
                              "(#[0-9a-f]{6})[\s]+(#[0-9a-f]{6})")
    figure_match = figure_regex.match(line)
    if figure_match is None:
        return None
    coords_str = figure_match.group(1).strip('<').strip('>')
    coords_lst = coords_str.split()
    if len(coords_lst) != 4:
        return None
    try:
        coords = [float(coord) for coord in coords_lst]
        border_size = float(figure_match.group(2))
    except ValueError:
        return None
    border_color = figure_match.group(3)
    fill_color = figure_match.group(4)
    return FigureInfo(figure_type="oval", coords=coords,
                      border_size=border_size,
                      border_color=border_color,
                      fill_color=fill_color)


def text_from_figure(figure: FigureInfo) -> str:
    ''' Print a figure to the text
    '''
    return f"{figure.figure_type} <{figure.coords[0]} {figure.coords[1]} " +\
           f"{figure.coords[2]} {figure.coords[3]}> {figure.border_size} " +\
           f"{figure.border_color} {figure.fill_color}"


def is_point_in_rectangle(point_x: float, point_y: float,
                          coords: t.List[float]) -> bool:
    # Get the top left and bottom right rectangle corners
    if coords[0] > coords[2]:
        coords[0], coords[2] = coords[2], coords[0]
    if coords[1] > coords[3]:
        coords[1], coords[3] = coords[3], coords[1]
    return (point_x >= coords[0] and point_x <= coords[2]
            and point_y >= coords[1] and point_y <= coords[3])


class GraphEditorFrame(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.new_coord = []
        self.figures_lst = []
        self.is_dragged_figure = False
        self.grid(sticky=tk.N+tk.S+tk.E+tk.W)
        self.create_widgets()

    def create_widgets(self):
        ''' Create widgets
        '''
        BUTTON_WIDTH = 5
        BUTTON_HEIGHT = 1
        TEXTEDITOR_LINEHEIGHT = 26
        TEXTEDITOR_CHARACTERWIDTH = 60
        GRAPHEDITOR_HEIGHT = 200
        GRAPHEDITOR_WIDTH = 400
        # Texteditor spans one row more than graph editor
        TEXTEDITOR_ROWSPAN = 20
        TEXTEDITOR_COLUMNSPAN = 30
        GRAPHEDITOR_COLUMNSPAN = 10
        assert(GRAPHEDITOR_COLUMNSPAN > 5)
        top = self.winfo_toplevel()
        # Enable scaling
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)
        for row_idx in range(TEXTEDITOR_ROWSPAN+2):
            self.rowconfigure(row_idx, weight=1)
        for column_idx in range(TEXTEDITOR_COLUMNSPAN+GRAPHEDITOR_COLUMNSPAN):
            self.columnconfigure(column_idx, weight=1)
        # Texteditor interface
        self.filename_label = tk.Label(self, text='image.txt')
        self.filename_label.grid(row=0, column=0,
                                 columnspan=TEXTEDITOR_COLUMNSPAN)
        # Grapheditor interface
        self.inkcolor_button = tk.Button(self, text='Ink')
        self.bordersize_entry = tk.Spinbox(self, text='2', width=4)
        self.oval_menubutton = tk.Menubutton(self, text='Oval',
                                             width=BUTTON_WIDTH,
                                             height=BUTTON_HEIGHT)
        self.figure_menu = tk.Menu(self)
        self.figure_menu.add_checkbutton(label='Oval')
        self.oval_menubutton['menu'] = self.figure_menu
        self.mousepos_label = tk.Label(self, text='0:0')

        # Grapheditor interface location
        self.inkcolor_button.grid(row=0, column=TEXTEDITOR_COLUMNSPAN + 1,
                                  rowspan=2)
        self.bordersize_entry.grid(row=0, column=TEXTEDITOR_COLUMNSPAN + 2,
                                   rowspan=2)
        self.oval_menubutton.grid(row=0, column=TEXTEDITOR_COLUMNSPAN + 3,
                                  rowspan=2)
        self.mousepos_label.grid(row=0, column=TEXTEDITOR_COLUMNSPAN + 4,
                                 rowspan=2)

        # Texteditor interface
        self.text_editor = tk.Text(self, width=TEXTEDITOR_CHARACTERWIDTH,
                                   height=TEXTEDITOR_LINEHEIGHT)
        self.text_editor.grid(row=1, column=0, rowspan=TEXTEDITOR_ROWSPAN,
                              columnspan=TEXTEDITOR_COLUMNSPAN,
                              sticky=tk.N+tk.S+tk.E+tk.W)
        self.text_editor.tag_configure("red", foreground="#ff0000")
        # Update the image after the release of any key
        self.text_editor.bind("<KeyRelease>", self.on_text_changed)
        self.graph_editor = tk.Canvas(self, bg='#854116',
                                      width=GRAPHEDITOR_WIDTH,
                                      height=GRAPHEDITOR_HEIGHT)
        self.graph_editor.grid(row=2, column=TEXTEDITOR_COLUMNSPAN,
                               columnspan=GRAPHEDITOR_COLUMNSPAN,
                               rowspan=TEXTEDITOR_ROWSPAN - 1,
                               sticky=tk.N+tk.S+tk.E+tk.W)

        # Track the mouse to enable creating new ovals and dragging figures
        self.graph_editor.bind("<Button-1>", self.on_mouse_click)
        self.graph_editor.bind("<Motion>", self.on_mouse_motion)
        self.graph_editor.bind("<ButtonRelease-1>", self.on_mouse_release)
        # Add empty space to fix the first row buttons
        self.columnconfigure(TEXTEDITOR_COLUMNSPAN + 5,
                             minsize=GRAPHEDITOR_WIDTH - 5 * BUTTON_WIDTH,
                             weight=1)

        # Application control buttons
        self.quit_button = tk.Button(self, text='Quit', width=BUTTON_WIDTH,
                                     height=BUTTON_HEIGHT, command=self.quit)
        self.save_button = tk.Button(self, text='Save',
                                     width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                     command=self.save_text)
        self.load_button = tk.Button(self, text='Load',
                                     width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
                                     command=self.load_text)
        self.save_button.grid(row=TEXTEDITOR_ROWSPAN + 1, column=0,
                              sticky=tk.N+tk.S+tk.E+tk.W)
        self.load_button.grid(row=TEXTEDITOR_ROWSPAN + 1, column=1,
                              sticky=tk.N+tk.S+tk.E+tk.W)
        self.quit_button.grid(row=TEXTEDITOR_ROWSPAN + 1,
                              column=TEXTEDITOR_COLUMNSPAN +
                              GRAPHEDITOR_COLUMNSPAN - 1, sticky=tk.N+tk.S)

    def on_mouse_click(self, event):
        ''' Draw new oval or drag existing
        '''
        # Does the cursor lie on the existing figure
        # If so, drag it
        self.is_dragged_figure = False
        for figure_idx in range(len(self.figures_lst)):
            figure = self.figures_lst[figure_idx]
            if is_point_in_rectangle(event.x, event.y, figure.coords):
                self.is_dragged_figure = True
                # Drag this figure
                self.dragged_figure_idx = figure_idx
        if not self.is_dragged_figure:
            self.new_coord = [event.x, event.y]
            self.new_oval = self.graph_editor.create_oval(
                                event.x, event.y, event.x, event.y,
                                outline="#000000", fill="#ffffff"
                            )
        else:
            # From which point the dragging started
            self.drag_start_coords = (event.x, event.y)

    def on_mouse_motion(self, event):
        ''' Resize the new oval, or drag existing
        '''
        if len(self.new_coord) == 2:
            # The new oval is being created
            self.graph_editor.coords(self.new_oval,
                                     self.new_coord[0], self.new_coord[1],
                                     event.x, event.y)
        elif self.is_dragged_figure:
            # Currently dragging the figure
            x_offset = event.x - self.drag_start_coords[0]
            y_offset = event.y - self.drag_start_coords[1]
            figure = self.figures_lst[self.dragged_figure_idx]
            self.graph_editor.coords(
                self.canvas_figures[self.dragged_figure_idx],
                figure.coords[0] + x_offset,
                figure.coords[1] + y_offset,
                figure.coords[2] + x_offset,
                figure.coords[3] + y_offset
             )

    def on_mouse_release(self, event):
        ''' Save changes in the image to text
        '''
        if len(self.new_coord) == 2:
            # Create new oval
            self.new_coord.append(event.x)
            self.new_coord.append(event.y)
            self.graph_editor.coords(self.new_oval,
                                     self.new_coord[0], self.new_coord[1],
                                     event.x, event.y)
            assert(len(self.new_coord) == 4)
            new_figure = FigureInfo(figure_type="oval",
                                    coords=self.new_coord,
                                    border_size=1.0,
                                    border_color="#000000",
                                    fill_color="#ffffff")
            self.text_editor.insert(tk.END,
                                    text_from_figure(new_figure) + '\n')
        elif self.is_dragged_figure:
            # Delete existing entry and create new
            line_start = f"{self.dragged_figure_idx + 1}.0"
            line_end = f"{self.dragged_figure_idx + 1}.end+1c"
            self.text_editor.delete(line_start, line_end)
            # Update the coordinates
            figure = self.figures_lst[self.dragged_figure_idx]
            new_coords = self.figures_lst[self.dragged_figure_idx].coords
            x_offset = event.x - self.drag_start_coords[0]
            y_offset = event.y - self.drag_start_coords[1]
            new_coords[0] += x_offset
            new_coords[1] += y_offset
            new_coords[2] += x_offset
            new_coords[3] += y_offset
            # Insert new figure
            new_figure = FigureInfo(figure_type=figure.figure_type,
                                    coords=new_coords,
                                    border_size=figure.border_size,
                                    border_color=figure.border_color,
                                    fill_color=figure.fill_color)
            self.text_editor.insert(tk.END,
                                    text_from_figure(new_figure) + '\n')
        self.create_figures_lst()
        self.draw_figures()
        self.is_dragged_figure = False

    def on_text_changed(self, event):
        ''' When text in the widger changes,
        update the figure list and highlights
        '''
        # Get input from the text widget
        # Get adds a newline, so delete it
        editor_input = self.text_editor.get("1.0", "end-1c")
        lines = editor_input.split('\n')
        tk_idx = tk.IntVar()
        self.figures_lst = []
        for line, line_idx in zip(lines, range(len(lines))):
            line_start = f"{line_idx+1}.0"
            line_end = f"{line_idx+1}.end"
            figure = figure_from_text(line)
            if figure is None:
                self.text_editor.tag_add("red", line_start, line_end)
            else:
                self.text_editor.tag_remove("red", line_start, line_end)
                self.figures_lst.append(figure)
        self.draw_figures()

    def create_figures_lst(self):
        ''' Create list of figures
        '''
        # Get input from the text widget
        # Get adds a newline, so delete it
        editor_input = self.text_editor.get("1.0", "end-1c")
        lines = editor_input.split('\n')
        self.figures_lst = []
        for line in lines:
            figure = figure_from_text(line)
            if figure is not None:
                self.figures_lst.append(figure)

    def draw_figures(self):
        ''' Draw figures from the figure list
        '''
        # Clear all previously drawn solution
        # Not optimal, better update them
        self.graph_editor.delete("all")
        self.canvas_figures = []
        for figure in self.figures_lst:
            if figure.figure_type == "oval":
                self.canvas_figures.append(
                    self.graph_editor.create_oval(
                        figure.coords[0], figure.coords[1],
                        figure.coords[2], figure.coords[3],
                        fill=figure.fill_color, outline=figure.border_color,
                        width=figure.border_size
                    )
                )

    def save_text(self):
        pass

    def load_text(self):
        pass


if __name__ == "__main__":
    graph_editor_frame = GraphEditorFrame()
    graph_editor_frame.master.title('Graph Edit')
    graph_editor_frame.mainloop()
