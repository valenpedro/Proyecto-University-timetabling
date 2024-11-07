import tkinter as tk
from tkinter import ttk, messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class TimetablingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("University Timetabling")
        self.root.geometry("1200x800")

        # Data storage
        self.courses = []
        self.students = []
        self.enrollment_matrix = []  # 1 indicates student is enrolled in course
        self.graph = nx.Graph()
        
        # Create main containers
        self.create_input_frame()
        self.create_matrix_frame()
        self.create_graph_frame()

    def create_input_frame(self):
        input_frame = ttk.LabelFrame(self.root, text="Input Data", padding="10")
        input_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

        # Course input
        ttk.Label(input_frame, text="Course name:").grid(row=0, column=0, padx=5, pady=5)
        self.course_entry = ttk.Entry(input_frame)
        self.course_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(input_frame, text="Add Course", command=self.add_course).grid(row=0, column=2, padx=5, pady=5)

        # Student input
        ttk.Label(input_frame, text="Student name:").grid(row=1, column=0, padx=5, pady=5)
        self.student_entry = ttk.Entry(input_frame)
        self.student_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(input_frame, text="Add Student", command=self.add_student).grid(row=1, column=2, padx=5, pady=5)

        # Generate and solve buttons
        ttk.Button(input_frame, text="Generate Graph", command=self.generate_graph).grid(row=2, column=0, columnspan=3, pady=10)
        ttk.Button(input_frame, text="Solve Timetable", command=self.solve_timetable).grid(row=3, column=0, columnspan=3, pady=5)

    def create_matrix_frame(self):
        self.matrix_frame = ttk.LabelFrame(self.root, text="Enrollment Matrix", padding="10")
        self.matrix_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.update_matrix_view()

    def create_graph_frame(self):
        self.graph_frame = ttk.LabelFrame(self.root, text="Conflict Graph", padding="10")
        self.graph_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=5, sticky="nsew")
        
        # Create matplotlib figure
        self.figure, self.ax = plt.subplots(figsize=(6, 6))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def add_course(self):
        course = self.course_entry.get().strip()
        if course and course not in self.courses:
            self.courses.append(course)
            self.course_entry.delete(0, tk.END)
            # Update enrollment matrix
            if self.students:
                for i in range(len(self.enrollment_matrix)):
                    self.enrollment_matrix[i].append(0)
            self.update_matrix_view()

    def add_student(self):
        student = self.student_entry.get().strip()
        if student and student not in self.students:
            self.students.append(student)
            self.student_entry.delete(0, tk.END)
            # Update enrollment matrix
            self.enrollment_matrix.append([0] * len(self.courses))
            self.update_matrix_view()

    def update_matrix_view(self):
        # Clear existing matrix view
        for widget in self.matrix_frame.winfo_children():
            widget.destroy()

        # Create headers
        ttk.Label(self.matrix_frame, text="Students/Courses").grid(row=0, column=0, padx=5, pady=5)
        for j, course in enumerate(self.courses):
            ttk.Label(self.matrix_frame, text=course).grid(row=0, column=j+1, padx=5, pady=5)

        # Create checkbuttons for enrollment
        for i, student in enumerate(self.students):
            ttk.Label(self.matrix_frame, text=student).grid(row=i+1, column=0, padx=5, pady=5)
            for j in range(len(self.courses)):
                var = tk.BooleanVar(value=bool(self.enrollment_matrix[i][j]))
                cb = ttk.Checkbutton(self.matrix_frame, variable=var, 
                                   command=lambda i=i, j=j, var=var: self.toggle_enrollment(i, j, var))
                cb.grid(row=i+1, column=j+1, padx=5, pady=5)

    def toggle_enrollment(self, i, j, var):
        self.enrollment_matrix[i][j] = int(var.get())

    def generate_graph(self):
        self.graph.clear()
        # Add nodes (courses)
        for course in self.courses:
            self.graph.add_node(course)
        
        # Add edges (conflicts between courses)
        for i in range(len(self.courses)):
            for j in range(i + 1, len(self.courses)):
                # Check if any student is enrolled in both courses
                for student_enrollments in self.enrollment_matrix:
                    if student_enrollments[i] and student_enrollments[j]:
                        self.graph.add_edge(self.courses[i], self.courses[j])
                        break

        self.draw_graph()

    def draw_graph(self):
        self.ax.clear()
        pos = nx.spring_layout(self.graph)
        nx.draw(self.graph, pos, ax=self.ax, with_labels=True, 
                node_color='lightblue', node_size=1500, font_size=8)
        self.canvas.draw()

    def greedy_coloring(self):
        colors = {}
        # Sort vertices by degree in descending order
        vertices = sorted(self.graph.nodes(), key=lambda x: self.graph.degree(x), reverse=True)
        
        for vertex in vertices:
            # Get colors of neighbors
            neighbor_colors = {colors.get(neighbor) 
                             for neighbor in self.graph.neighbors(vertex) 
                             if neighbor in colors}
            
            # Find first available color
            color = 0
            while color in neighbor_colors:
                color += 1
            colors[vertex] = color
            
        return colors

    def solve_timetable(self):
        if not self.graph.nodes():
            messagebox.showwarning("Warning", "Please generate the graph first!")
            return
            
        colors = self.greedy_coloring()
        
        # Draw colored graph
        self.ax.clear()
        pos = nx.spring_layout(self.graph)
        nx.draw(self.graph, pos, ax=self.ax, with_labels=True,
                node_color=[colors[node] for node in self.graph.nodes()],
                node_size=1500, font_size=8, cmap=plt.cm.rainbow)
        self.canvas.draw()
        
        # Show results
        result_window = tk.Toplevel(self.root)
        result_window.title("Timetable Solution")
        result_window.geometry("400x400")
        
        text_widget = tk.Text(result_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        text_widget.insert(tk.END, "Timetable Assignment:\n\n")
        for course, time_slot in colors.items():
            text_widget.insert(tk.END, f"Course: {course}\nTime Slot: {time_slot + 1}\n\n")
        
        text_widget.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = TimetablingApp(root)
    root.mainloop()