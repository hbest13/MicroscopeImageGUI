import sys
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtMultimedia import *
from PySide6.QtMultimediaWidgets import *
from PySide6.QtCore import *
import os
from os import listdir
import csv
from datetime import datetime
from operator import itemgetter
import pathlib

# Create a class for the scroll area which will contain all the displayed images and information for the user
class ScrollWindow(QWidget):
    def __init__(self, imgPath=None, parent=None):
        super(ScrollWindow, self).__init__()
        self.setParent(parent)
        self.scroll = QScrollArea()
        self.scroll_widget = QWidget()
        self.layout_two = QGridLayout()
        self.scroll_widget.setLayout(self.layout_two)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)  
        self.scroll.setWidget(self.scroll_widget) 
        self.layout_main = QGridLayout()
        self.setLayout(self.layout_main)
        self.layout_main.addWidget(self.scroll)
        if getattr(sys, 'frozen', False):
            self.application_path = os.path.dirname(sys.executable)
        elif __file__:
            self.application_path = os.path.dirname(__file__)
        #self.hips_data_path = "C:/Users/hanna/OneDrive - University of California, Davis/Crocker/MicroscopeImages/HIPSdata2020Microscope.csv"
        with open(os.path.join(self.application_path, 'HIPSdata2020Microscope.csv')) as csv_file:
          self.hips_csv = csv.reader(csv_file, delimiter=',')
          self.first_row = next(self.hips_csv, None)
          self.data = list(self.hips_csv)

    # Create a generic function to display the images in the scroll area
    def display_general_image(self, ordered_image_list, number_across = 2):
      i = 1
      x = 0
      # This for loops clears all the previously displayed images when new ones are selected or they are sorted differently.
      # This is done by setting the parents of the widgets containing the images and their labels to None
      for i in reversed(range(main.image_display_area.layout_two.count())): 
        main.image_display_area.layout_two.itemAt(i).widget().setParent(None)
      # This for loop goes through all the individual images lists contained within the larger ordered_image_list
      # For each image it creates a label widget for the picture and one for the image information
      for list in ordered_image_list:
        self.image_label = QLabel(self)
        self.image_info_label = QLabel(self)
        self.image_info_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        # This if statement places the image widgets in column numbers based on the grid layout selected by the user
        if x < number_across:
          main.image_display_area.layout_two.addWidget(self.image_label, i, x, alignment = Qt.AlignCenter)
          main.image_display_area.layout_two.addWidget(self.image_info_label, i + 1, x, alignment = Qt.AlignCenter)
          x += 1
        else:
          i += 2
          x = 0
        pixmap = QPixmap(list[2])
        scaled_pixmap = pixmap.scaled(((main.image_display_area.width())/number_across) - (100/number_across), 500, Qt.KeepAspectRatio)
        self.image_label.setPixmap(scaled_pixmap)
        s = "    "
        self.image_info_label.setText("Site:  " + list[4] + s + "Sample Date:  " +
                                        list[1].strftime('%m/%d/%Y') + s +
                                        "\n" + "PM2.5:  " + str(list[8]) + s + "fAbs:  " +
                                        str(list[5]) + s + "Fe:  " + str(list[6]) + "\n" + "K:  " + str(list[7]) + s +
                                        "EC: " + str(list[9]) + s + "OC/EC: " + str(list[11]) + "\n")
    
    # Function to loop through the CSV data to find the image's site name
    def retrieve_site_name(self, filter_ID):
      for row in self.data:
        if filter_ID == row[0]:
          if 'Fe' == row[3]:
            self.site_name = row[1]
      return self.site_name

    # Function to loop through the CSV to find the image's data and parameter values
    def retrieve_filter_data(self, filter_ID, sample_date, site):
      for row in self.data:
        if site == row[1]:
          if sample_date == datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S.%f'):
            if row[3] == 'EC':
              self.EC = row[4]
            elif row[3] == 'OC':
              self.OC = row[4]
        if filter_ID in row[0]:
          if "fAbs" == row[3]:
            self.fAbs = row[4]
          elif 'Fe' == row[3]:
            self.Fe = row[4]
          elif "K" == row[3]:
            self.K = row[4]
          elif 'PM2.5' == row[3]:
            self.PM25 = row[4]
      return self.fAbs, self.Fe, self.K, self.PM25, self.EC, self.OC

    # This is a function to display all the images in the IMPROVE folder. It is currently the only option 
    # available to the user when selecting which images to display
    def display_all_images(self):
      self.image_list = []
      folder_dir = os.path.join(self.application_path, 'IMPROVE')
      for study in os.listdir(folder_dir):
        for image in os.listdir(folder_dir + '/' + study):
          if image.endswith(".csv"):
            temporary_image_info_list = []
            self.csv_rows = []
            name_start = image.strip('.csv')
            with open(folder_dir + '/' + study + '/' + image) as csv_file:
              csv_reader = csv.reader(csv_file, delimiter=',')
              for row in csv_reader:
                self.csv_rows.append(row)
              date_time = datetime.strptime(self.csv_rows[2][1], '%m/%d/%Y')
              temporary_image_info_list.append(self.csv_rows[0][1])
              temporary_image_info_list.append(date_time)
              temp_site_name = self.retrieve_site_name(self.csv_rows[0][1])
              temp_filter_data = self.retrieve_filter_data(self.csv_rows[0][1], date_time, temp_site_name)
              for image in os.listdir(folder_dir + '/' + study):
                if (image.endswith(".jpg")) and (image.strip(".jpg") == name_start):
                  temporary_image_info_list.append((folder_dir + '/' + study + '/' + image))
                  temporary_image_info_list.append(study)
                  temporary_image_info_list.append(temp_site_name)
                  x = 0
                  #for index in list(range(x)):
                  while x < 6:
                    try:
                      temporary_image_info_list.append(float(temp_filter_data[x]))
                      x += 1
                    except:
                      temporary_image_info_list.append(0000)
                      x += 1
                  try:
                    self.OC_EC_ratio = (temporary_image_info_list[10]/temporary_image_info_list[9])
                    temporary_image_info_list.append(round(float(self.OC_EC_ratio), 3))
                  except:
                    self.OC_EC_ratio = 0000
                    temporary_image_info_list.append(self.OC_EC_ratio)
            self.image_list.append(temporary_image_info_list)
      return self.image_list

    # Function to check which images the user has selected to be displayed from the dialog box. The only
    # current option is 'all images', but hopefully different parameter option such as date, site, etc... will be added
    def display_image(self, start_date = 0, end_date = 0):
      # Check to see if the 'all images' box is checked
      if main.tool_bar_display.dialog.all_checkbox.isChecked():
        self.display_general_image(self.display_all_images(), 2)
      else:
        print('hello')


# Create a class for the top toolbar which will contain methods to load the images and sort them
class ToolBar(QWidget):
    def __init__(self, parent=None):
        super(ToolBar, self).__init__()
        self.setParent(parent)
        self.tool_bar = QToolBar()
        self.selection_button = QPushButton("Select Images")
        self.selection_button.clicked.connect(self.choose_images)
        #self.selection_button.clicked.connect(self.pick_file)
        self.tool_bar.addWidget(self.selection_button)
        self.tool_bar.addSeparator()
        self.grid_size = QComboBox()
        self.grid_size.activated.connect(self.make_grid_size)
        self.grid_size.addItems(["Layout", "2 Across", "3 Across", "4 Across"])
        self.current_grid = 2
        self.tool_bar.addWidget(self.grid_size)
        self.tool_bar.addSeparator()
        self.date_combo = QComboBox()
        self.date_combo.activated.connect(self.sort_by_date)      
        self.date_combo.addItems(["Sort by Sample Date", "Ascending Date", "Descending Date"])
        self.tool_bar.addWidget(self.date_combo)
        self.tool_bar.addSeparator()
        self.site_combo = QComboBox()
        self.site_combo.activated.connect(self.sort_by_site)
        self.site_combo.addItems(["Sort by Site", "A to Z", "Z to A"])
        self.tool_bar.addWidget(self.site_combo)
        self.tool_bar.addSeparator()
        self.parameter_combo = QComboBox()
        self.parameter_combo.activated.connect(self.sort_by_parameter)
        self.parameter_combo.addItems(["Sort by Parameter", "fAbs", "PM2.5", "Fe", "K", "EC", "OC/EC"])
        self.tool_bar.addWidget(self.parameter_combo)
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.tool_bar)

    # Function to pick image files from file dialog box - function not currently in use
    def pick_file(self):
      self.file_dialog = QFileDialog()
      self.folder_path = self.file_dialog.getExistingDirectory(None, "Select Folder")
      self.folder_path
      return self.folder_path

    # Function to execute the image selection dialog box - it is an instance of the ImageSelection class
    def choose_images(self):
        # call instance of dialog choice class
        self.dialog = ImageSelection()
        #self.dialog = ImageSelection()
        self.dialog.exec()

    # Function to sort the images by ascending or descending date
    # Sorting by date will set the other sort option combo boxes back to their original state
    def sort_by_date(self):
      self.image_list = main.image_display_area.image_list
      current_index = self.date_combo.currentIndex()
      sorted_list = sorted(self.image_list, key = itemgetter(1))
      reverse_sorted_list = sorted(self.image_list, key = itemgetter(1), reverse = True)
      for i in reversed(range(main.image_display_area.layout_two.count())): 
        main.image_display_area.layout_two.itemAt(i).widget().setParent(None)
      if current_index == 0:
        main.image_display_area.display_general_image(self.image_list, self.current_grid)
      elif current_index == 1:
        self.site_combo.setCurrentText("Sort by Site")
        self.parameter_combo.setCurrentText("Sort by Parameter")
        main.image_display_area.display_general_image(sorted_list, self.current_grid)
      elif current_index == 2:
        self.site_combo.setCurrentText("Sort by Site")
        self.parameter_combo.setCurrentText("Sort by Parameter")
        main.image_display_area.display_general_image(reverse_sorted_list, self.current_grid)

    # Function to sort by site - only alphabtically or reverse alphabetically
    def sort_by_site(self):
        self.image_list = main.image_display_area.image_list
        current_index = self.site_combo.currentIndex()
        sorted_list = sorted(self.image_list, key = itemgetter(4))
        reverse_sorted_list = sorted(self.image_list, key = itemgetter(1), reverse = True)
        for i in reversed(range(main.image_display_area.layout_two.count())): 
            main.image_display_area.layout_two.itemAt(i).widget().setParent(None)
        if current_index == 0:
            main.image_display_area.display_general_image(self.image_list, self.current_grid)
        elif current_index == 1:
            self.date_combo.setCurrentText("Sample Date")
            self.parameter_combo.setCurrentText("Sort by Parameter")
            main.image_display_area.display_general_image(sorted_list, self.current_grid)
            #call general display image function with start and end date set to the oldest and newest dates that are currently displayed,
        elif current_index == 2:
            self.date_combo.setCurrentText("Sample Date")
            self.parameter_combo.setCurrentText("Sort by Parameter")
            main.image_display_area.display_general_image(reverse_sorted_list, self.current_grid)

    # Function to sort by the image's various parameters
    def sort_by_parameter(self):
      self.image_list = main.image_display_area.image_list
      current_index = self.parameter_combo.currentIndex()
      for i in reversed(range(main.image_display_area.layout_two.count())): 
          main.image_display_area.layout_two.itemAt(i).widget().setParent(None)
      if current_index == 0:
        main.image_display_area.display_general_image(self.image_list, self.current_grid)
      # Index 1 is fAbs
      elif current_index == 1:
        self.date_combo.setCurrentText("Sample Date")
        self.site_combo.setCurrentText("Sort by Site")
        sorted_list = sorted(self.image_list, key = itemgetter(5), reverse = True)
        main.image_display_area.display_general_image(sorted_list, self.current_grid)
      # Index 2 is PM2.5
      elif current_index == 2:
        self.date_combo.setCurrentText("Sample Date")
        self.site_combo.setCurrentText("Sort by Site")
        sorted_list = sorted(self.image_list, key = itemgetter(8), reverse = True)
        main.image_display_area.display_general_image(sorted_list, self.current_grid)
      # Index 3 is Fe
      elif current_index == 3:
        self.date_combo.setCurrentText("Sample Date")
        self.site_combo.setCurrentText("Sort by Site")
        sorted_list = sorted(self.image_list, key = itemgetter(6), reverse = True)
        main.image_display_area.display_general_image(sorted_list, self.current_grid)
      # Index 4 is K
      elif current_index == 4:
        self.date_combo.setCurrentText("Sample Date")
        self.site_combo.setCurrentText("Sort by Site")
        sorted_list = sorted(self.image_list, key = itemgetter(7), reverse = True)
        main.image_display_area.display_general_image(sorted_list, self.current_grid)
      # Index 5 is EC
      elif current_index == 5:
        self.date_combo.setCurrentText("Sample Date")
        self.site_combo.setCurrentText("Sort by Site")
        sorted_list = sorted(self.image_list, key = itemgetter(9), reverse = True)
        main.image_display_area.display_general_image(sorted_list, self.current_grid)
      # Index 6 is OC/EC
      elif current_index == 6:
        self.date_combo.setCurrentText("Sample Date")
        self.site_combo.setCurrentText("Sort by Site")
        sorted_list = sorted(self.image_list, key = itemgetter(11), reverse = True)
        main.image_display_area.display_general_image(sorted_list, self.current_grid)

    # Function to retrieve the user's desired image grid layout size from the layout combo box
    def make_grid_size(self):
      self.image_list = main.image_display_area.image_list
      current_index = self.grid_size.currentIndex()
      # Index 0 reverts to the default which is 2 across
      if current_index == 0:
        self.current_grid = 2
        main.image_display_area.display_general_image(self.image_list, 2)
      # Index 1 is 2 images across
      if current_index == 1:
        self.current_grid = 2
        main.image_display_area.display_general_image(self.image_list, 2)
      # Index 2 is 3 images across
      if current_index == 2:
        self.current_grid = 3
        main.image_display_area.display_general_image(self.image_list, 3)
      # Index 3 is 4 images across
      if current_index == 3:
        self.current_grid = 4
        main.image_display_area.display_general_image(self.image_list, 4)


# Create a class for the dialog box that the user will use to select which images to display
class ImageSelection(QDialog):
    def __init__(self):
        super(ImageSelection, self).__init__()
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.resize(500, 100)
        self.setWindowTitle("Choose Images")

        all_label = QLabel("All Photos: ")
        self.layout.addWidget(all_label, 0, 0, alignment=Qt.AlignTop)
        self.all_checkbox = QCheckBox("All Images")
        self.layout.addWidget(self.all_checkbox, 1, 0, alignment=Qt.AlignTop)

        # site_label = QLabel("Choose Site(s):")
        # self.layout.addWidget(site_label, 2, 0, alignment=Qt.AlignTop)
        # site_button = QCheckBox("All")
        # self.layout.addWidget(site_button, 3, 0, alignment=Qt.AlignTop)
        # site_button_one = QCheckBox("Site 1")
        # self.layout.addWidget(site_button_one, 3, 1, alignment=Qt.AlignTop)

        # start_date_label = QLabel("Choose Start Date:")
        # self.layout.addWidget(start_date_label, 4, 0)
        # end_date_label = QLabel("Choose End Date:")
        # self.layout.addWidget(end_date_label, 4, 1)
        # self.start_date = QDateEdit(calendarPopup=True)
        # self.layout.addWidget(self.start_date, 5, 0)
        # self.end_date = QDateEdit(calendarPopup=True)
        # self.layout.addWidget(self.end_date, 5, 1)

        done_button = QPushButton('Done')
        #self.layout.addWidget(done_button, 6, 1, alignment=Qt.AlignBottom)
        self.layout.addWidget(done_button, 2, 1, alignment=Qt.AlignBottom)
        #done_button.clicked.connect(self.get_date_input)
        done_button.clicked.connect(self.close)
        done_button.clicked.connect(main.image_display_area.display_image)

    # Function to get desired image start and end dates from the selection dialog box - function not currently in use
    def get_date_input(self):
      # Returns date in (year, month, day) format; 1/14/2000 = (2000, 1, 14)
      self.selected_start_date = self.start_date.date()
      self.selected_end_date = self.end_date.date()


# Create a class for the main window of the app, this window will contain instances of all the other classes within and
# thus contain all their widgets as well
class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('Microscope Images and HIPS Data')
        self.mainLayout = QGridLayout()
        self.setLayout(self.mainLayout)
        # Create an instance of the scroll area where the images will be displayed
        self.image_display_area = ScrollWindow(self)
        self.mainLayout.addWidget(self.image_display_area, 1, 0)
        # Create an instance of the toolbar and display it one row above the scroll area (the top of the main window)
        self.tool_bar_display = ToolBar(self)
        self.mainLayout.addWidget(self.tool_bar_display, 0, 0, alignment=Qt.AlignTop)


# Initiate the application and create an instance of the mainwindow
app = QApplication(sys.argv)
main = MainWindow()
main.show()
sys.exit(app.exec())
