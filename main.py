from tkinter import Tk, Frame, Label, LabelFrame, Entry, INSERT, Button, Listbox, Scrollbar, RIGHT, StringVar
from bs4 import BeautifulSoup
import requests

def soup_requests(link):
    req = requests.get(link)
    soup = BeautifulSoup(req.content, "html.parser")
    return soup

def soup_get_text(soup):
    return soup.getText().strip().encode("ascii", "ignore").decode()

colors = ['cadet blue', 'medium aquamarine', 'aquamarine',  'LemonChiffon4', 'dark turquoise', 'cornsilk2','cornsilk4', 'honeydew2','medium turquoise','dodger blue', 'dark orchid',  'turquoise', 'cyan', 'dark violet', 'blue violet', 'purple', 'pale turquoise']

week_days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

time_space = [  "09:00-09:30", "09:30-10:00", 
                "10:00-10:30", "10:30-11:00", 
                "11:00-11:30", "11:30-12:00", 
                "12:00-12:30", "12:30-13:00", 
                "13:00-13:30", "13:30-14:00", 
                "14:00-14:30", "14:30-15:00", 
                "15:00-15:30", "15:30-16:00", 
                "16:00-16:30", "16:30-17:00", 
                "17:00-17:30", "17:30-18:00", 
                "18:00-18:30", "18:30-19:00", 
                "19:00-19:30", "19:30-20:00", 
                "20:00-20:30", "20:30-21:00", 
                "21:00-21:30", "21:30-22:00"]

def start_end_time(time):
    parsed = time.split("-")
    times = [i for i, t in enumerate(time_space) if parsed[0] in t or parsed[1] in t]
    if len(times) == 3:
        if(parsed[0] == "09:00"):
            return [times[0], times[2]]
        else:
            return [times[1], times[2]]
    else:
        return [times[1], times[3]]


class Course:
    def get_tuple_times(self):
        len_days = len(self.days)
        len_times = len(self.times)
        if len_days > len_times:
            return [(day, self.times[0]) for day in self.days]
        elif len_times > len_days:
            return [(self.days[0], time) for time in self.times]
        else:
            return list(zip(self.days, self.times))

    def get_days(self):
        return [week_days.index(d) for d in self.days]

    def __init__(self, name, days, times):
        self.name = name
        self.days = days.split()
        self.times = times.split()

    def set_color(self, color):
        self.color = color

    def __str__(self):
        return self.name + " " + " ".join(self.days) + " " +" ".join(self.times)


class MyCell(Label):

    def __init__(self, master, row, col, bg="green", text="", padx=0, pady=0):
        super().__init__(master, bg=bg, text=text, font="Arial 11 bold")
        self.grid(sticky="nsew", row=row, column=col, padx=padx, pady=pady)

class TimeTable(Frame):

    def find_collision(self, rows, col, name):
        collision_list = []
        for row in range(rows[0], rows[1]):
            cell = self.grid_slaves(row=row+1, column=col+1)[0]
            text = cell["text"]
            if text != "" and text != name:
                collision_list.append(row)
        return collision_list 

    def change_cell(self, row, col, text="", bg="green"):
        cell = self.grid_slaves(row=row+1, column=col+1)[0]
        if text != "-1":
            cell.config(text=text, bg=bg)
        else:
            cell.config(bg=bg)

    def fill_table(self):
        for col in range(len(week_days) + 1):
            self.columnconfigure(col, weight=1)

        for row in range(len(time_space) + 1):
            for col in range(len(week_days) + 1):
                if row == 0:
                    if col == 0:
                        MyCell(self, row, col, "black")
                    else:
                        MyCell(self, row, col, "cyan", week_days[col-1])
                elif col == 0:
                    MyCell(self, row, col, "cyan", time_space[row-1])
                else:
                    MyCell(self, row, col, padx=2, pady=2)

        self.rowconfigure(row, weight=1)

    def reset_table(self):
        for row in range(0, len(time_space)):
            for col in range(0, len(week_days)):
                self.change_cell(row, col)

    def __init__(self, master):
        super().__init__(master)
        self.fill_table()


class GUI:

    def fill_all(self):
        for course in self.selected_course_list:
            self.fill_table(course, course.color)

    def fill_table(self, course, bg="green", isRemove=False):
        for time in course.get_tuple_times():
            col = week_days.index(time[0])
            rows = start_end_time(time[1])
            if "22:00" in time[1]:
                rows[1]+=1
            if not isRemove:
                collision_list = self.table.find_collision(rows, col, course.name)
            else:
                collision_list = []
            for row in range(rows[0], rows[1]):
                if isRemove:
                    self.table.change_cell(row, col, "", bg)
                else:
                    if row in collision_list:
                        self.table.change_cell(row, col, "-1", "red")
                    else:
                        self.table.change_cell(row, col, course.name, bg)

    def fetch_courses(self):
        url = self.url_text.get()
        if url != "":
            self.color_num = 0
            self.selected_course_list = []
            self.current_course = None
            self.course_list = []
            self.courses_listbox.delete(0,"end")
            soup = soup_requests(url)
            rows = soup.select(".MsoTableGrid > tbody > tr")
            for row in rows:
                cells = row.select("td")
                cellTexts = [soup_get_text(cells[0]), soup_get_text(cells[2]), soup_get_text(cells[3])]
                i = 0
                if cellTexts[0]!="" and cellTexts[1]!="" and cellTexts[2]!="":
                    i+=1
                    course = Course(cellTexts[0], cellTexts[1], cellTexts[2])
                    self.course_list.append(course)
            self.course_list = sorted(self.course_list,key=lambda course: str(course))
            self.filtered_course_list = self.course_list
            for i,course in enumerate(self.course_list):
                self.courses_listbox.insert(i+1, course)

    def add_course(self):
        if self.current_course:
            if self.current_course not in self.selected_course_list:
                for time in self.current_course.get_tuple_times():
                    col = week_days.index(time[0])
                    rows = start_end_time(time[1])
                    collision_list = self.table.find_collision(rows, col, self.current_course.name)
                    if len(collision_list) != 0:
                        self.error_label.config(text="Cloud not be added", bg="red")
                        return

                if self.color_num == len(colors)-1:
                    self.color_num = 0
                else:
                    self.color_num += 1
                self.current_course.set_color(colors[self.color_num])
                self.selected_course_list.append(self.current_course)
                size = len(self.selected_course_list)
                self.fill_table(self.current_course, colors[self.color_num])
                self.cur_courses_listbox.insert(size, self.current_course)
                self.current_course = None

    def add_list_select(self, event):
        self.error_label.config(text="", bg=self.main_frame["bg"])
        widget = event.widget
        selecteds = widget.curselection()
        if selecteds:
            self.current_course = self.filtered_course_list[selecteds[0]]
            if self.current_course in self.selected_course_list:
                return
            
            self.table.reset_table()
            self.fill_all()
            self.fill_table(self.current_course, "yellow")

    def remove_course(self):
        if self.remove_list_selected != None:
            self.cur_courses_listbox.delete(self.remove_list_selected_index)
            self.selected_course_list.remove(self.remove_list_selected)
            self.table.reset_table()
            self.fill_all()
            self.remove_list_selected = None

    def remove_list_select(self, event):
        widget = event.widget
        selecteds = widget.curselection()
        if selecteds:
            self.remove_list_selected_index = selecteds[0]
            self.remove_list_selected = self.selected_course_list[self.remove_list_selected_index]

    def uptade_list(self, *args):
        term = self.filter_var.get()
        if term == "":
            self.filtered_course_list = self.course_list
        else:
            term = term.lower()
            self.filtered_course_list = []
            for c in self.course_list:
                if term in c.name.lower():
                    self.filtered_course_list.append(c)
        self.courses_listbox.delete(0,"end")
        for i, c in enumerate(self.filtered_course_list):
            self.courses_listbox.insert(i+1, c)

    def __init__(self):
        self.main_window = Tk()
        self.main_window.title("Sehir Course Planner")
        self.main_window.minsize(1000, 800)

        self.main_frame = Frame(self.main_window)
        Label(self.main_frame, text="Sehir Course Planner", bg="black", fg="dodger blue", padx=2, pady=2, font="Area 20").pack(fill="x")

        #url
        self.url_frame = Frame(self.main_frame)
        Label(self.url_frame, text="Course Offerings Url:", font="Area 14").grid(row=0, column=0, padx=10)

        self.url_text = Entry(self.url_frame, font="Area 12", width=80)
        self.url_text.grid(row=0, column=1)
        self.url_text.insert(INSERT, "https://www.sehir.edu.tr/tr/duyurular/2019_2020_akademik_yili_bahar_donemi_ders_programi")

        Button(self.url_frame, text="Fetch Courses", command=self.fetch_courses).grid(row=0, column=2, padx=10)
        self.url_frame.pack(padx=15, pady=10)

        #course frame
        self.course_frame = LabelFrame(self.main_frame)

        self.course_left = Frame(self.course_frame)
        self.course_filter_frame = Frame(self.course_left)
        Label(self.course_filter_frame, text="Filter:", font="Area 12").grid(row=0, column=0)
        self.filter_var = StringVar()
        self.filter_var.trace("w", self.uptade_list)
        self.filter_entry = Entry(self.course_filter_frame, font="Area 12", textvariable=self.filter_var)
        self.filter_entry.grid(row=0, column=1)
        self.course_filter_frame.grid_columnconfigure(0, weight=1)
        self.course_filter_frame.grid_columnconfigure(1, weight=2)
        self.course_filter_frame.pack(fill="x",pady=5)
        self.course_left_listbox_frame = Frame(self.course_left)
        self.courses_scroll = Scrollbar(self.course_left_listbox_frame)
        self.courses_scroll.pack(side=RIGHT, fill="y")
        self.courses_listbox =  Listbox(self.course_left_listbox_frame, yscrollcommand=self.courses_scroll.set,  height=6)
        self.courses_listbox.bind("<<ListboxSelect>>", self.add_list_select)
        self.courses_listbox.pack(fill="x")
        self.courses_scroll.config(command=self.courses_listbox.yview)
        self.course_left_listbox_frame.pack(fill="x")
        self.course_left.grid(sticky="nsew", row=0, column=0, padx=10, pady=10)
        
        self.course_mid = Frame(self.course_frame)
        self.error_label = Label(self.course_mid)
        self.error_label.pack(fill="x")
        Button(self.course_mid, text="Add", command=self.add_course).pack(pady=10)
        Button(self.course_mid, text="Remove", command=self.remove_course).pack(pady=10)
        self.course_mid.grid(row=0, column=1)

        self.course_right = Frame(self.course_frame)
        Label(self.course_right, text="Selected Courses", font="Area 12").pack(fill="x")
        self.course_right_listbox_frame = Frame(self.course_right)
        self.selected_courses_scroll = Scrollbar(self.course_right_listbox_frame)
        self.selected_courses_scroll.pack(side=RIGHT, fill="y")
        self.cur_courses_listbox = Listbox(self.course_right_listbox_frame, yscrollcommand=self.selected_courses_scroll.set, height=6)
        self.cur_courses_listbox.bind("<<ListboxSelect>>", self.remove_list_select)
        self.cur_courses_listbox.pack(fill="x")
        self.selected_courses_scroll.config(command=self.cur_courses_listbox.yview)
        self.course_right_listbox_frame.pack(fill="x")
        self.course_right.grid(sticky="nsew", row=0, column=2, padx=10, pady=10)

        self.course_frame.grid_columnconfigure(0, weight=10)
        self.course_frame.grid_columnconfigure(1, weight=1)
        self.course_frame.grid_columnconfigure(2, weight=10)
        self.course_frame.pack(fill="x", padx=15, pady=10)

        self.table = TimeTable(self.main_frame)
        self.table.fill_table()
        self.table.pack(fill="x", padx=15, pady=10)
        self.main_frame.pack(fill="both", expand=True)
        

    def show(self):
        self.main_window.mainloop()

def main():
    gui = GUI()
    gui.show()

if __name__ == '__main__': main()