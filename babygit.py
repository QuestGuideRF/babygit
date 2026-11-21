import sys
import os
import subprocess
import webbrowser
import json
import platform
from PyQt6 .QtWidgets import (
QApplication ,QMainWindow ,QWidget ,QVBoxLayout ,QHBoxLayout ,QLabel ,QLineEdit ,QPushButton ,
QStackedWidget ,QFileDialog ,QMessageBox ,QProgressBar ,QListWidget ,QCheckBox ,QScrollArea ,
QListWidgetItem
)
from PyQt6 .QtCore import Qt ,QThread ,pyqtSignal
from PyQt6 .QtGui import QFont ,QIcon
class GitWorker (QThread ):
    progress =pyqtSignal (int )
    finished =pyqtSignal (bool ,str )
    def __init__ (self ,username ,email ,repo_url ,project_path ,commit_message ,selected_files ):
        super ().__init__ ()
        self .username =username
        self .email =email
        self .repo_url =repo_url
        self .project_path =project_path
        self .commit_message =commit_message
        self .selected_files =selected_files
    def run (self ):
        try :
            subprocess .run (["git","config","user.name",self .username ],cwd =self .project_path )
            subprocess .run (["git","config","user.email",self .email ],cwd =self .project_path )
            if not os .path .exists (os .path .join (self .project_path ,".git")):
                subprocess .run (["git","init"],cwd =self .project_path )
                subprocess .run (["git","branch","-M","main"],cwd =self .project_path )
            for file in self .selected_files :
                subprocess .run (["git","add",file ],cwd =self .project_path )
            subprocess .run (["git","commit","-m",self .commit_message ],cwd =self .project_path )
            result =subprocess .run (["git","remote","-v"],cwd =self .project_path ,capture_output =True ,text =True )
            if not result .stdout :
                subprocess .run (["git","remote","add","origin",self .repo_url ],cwd =self .project_path )
            branch_result =subprocess .run (["git","branch","--show-current"],cwd =self .project_path ,capture_output =True ,text =True )
            current_branch =branch_result .stdout .strip ()
            if current_branch !="main":
                subprocess .run (["git","branch","-M","main"],cwd =self .project_path )
            result =subprocess .run (["git","push","-u","origin","main"],cwd =self .project_path ,capture_output =True ,text =True )
            if result .returncode ==0 :
                self .finished .emit (True ,"Файлы успешно загружены в репозиторий!")
            else :
                self .finished .emit (False ,f"Ошибка при push:\n{result .stderr }")
        except Exception as e :
            self .finished .emit (False ,str (e ))
class GitInstaller (QThread ):
    finished =pyqtSignal (bool ,str )
    def run (self ):
        try :
            if platform .system ()=="Windows":
                result =subprocess .run (["winget","install","--id","Git.Git","-e","--source","winget"],
                capture_output =True ,text =True )
                if result .returncode ==0 :
                    self .finished .emit (True ,"Git успешно установлен!")
                else :
                    self .finished .emit (False ,"Не удалось установить Git автоматически. Пожалуйста, установите Git вручную с https://git-scm.com/downloads")
            else :
                self .finished .emit (False ,"Автоматическая установка Git поддерживается только на Windows. Пожалуйста, установите Git вручную.")
        except Exception as e :
            self .finished .emit (False ,f"Ошибка при установке Git: {str (e )}")
class MainWindow (QMainWindow ):
    def __init__ (self ):
        super ().__init__ ()
        self .setWindowTitle ("BabyGIT")
        self .setMinimumSize (900 ,500 )
        icon_path =os .path .join (os .path .dirname (os .path .abspath (__file__ )),"BabyGIT.ico")
        if os .path .exists (icon_path ):
            self .setWindowIcon (QIcon (icon_path ))
        if not self .check_git_installed ():
            self .install_git ()
        else :
            self .load_user_data ()
            self .init_ui ()
    def load_user_data (self ):
        self .user_data ={
        'username':'',
        'email':'',
        'repo_url':''
        }
        try :
            if os .path .exists ('user_data.json'):
                with open ('user_data.json','r',encoding ='utf-8')as f :
                    self .user_data =json .load (f )
        except Exception :
            pass
    def save_user_data (self ):
        try :
            with open ('user_data.json','w',encoding ='utf-8')as f :
                json .dump (self .user_data ,f ,ensure_ascii =False ,indent =2 )
        except Exception :
            pass
    def init_ui (self ):
        self .stacked =QStackedWidget ()
        self .setCentralWidget (self .stacked )
        self .init_screen1 ()
        self .init_screen2 ()
        self .stacked .setCurrentIndex (0 )
    def init_screen1 (self ):
        w =QWidget ()
        layout =QVBoxLayout (w )
        font =QFont ()
        font .setPointSize (16 )
        self .username_input =QLineEdit ()
        self .username_input .setPlaceholderText ("Никнейм")
        self .username_input .setFont (font )
        self .username_input .setText (self .user_data ['username'])
        self .email_input =QLineEdit ()
        self .email_input .setPlaceholderText ("Электронная почта")
        self .email_input .setFont (font )
        self .email_input .setText (self .user_data ['email'])
        self .repo_input =QLineEdit ()
        self .repo_input .setPlaceholderText ("URL-хранилище")
        self .repo_input .setFont (font )
        self .repo_input .setText (self .user_data ['repo_url'])
        self .next_btn =QPushButton ("Далее")
        self .next_btn .setEnabled (False )
        self .next_btn .setFont (font )
        self .next_btn .setMinimumHeight (40 )
        self .next_btn .clicked .connect (self .on_next_clicked )
        self .create_repo_btn =QPushButton ("Создать репозиторий на GitHub")
        self .create_repo_btn .setFont (font )
        self .create_repo_btn .setMinimumHeight (36 )
        self .create_repo_btn .clicked .connect (self .open_github_repos )
        tip =QLabel ("1. Введите свой никнейм и электронную почту.\n"
        "2. Нажмите на кнопку выше — откроется страница ваших репозиториев на GitHub.\n"
        "3. Нажмите 'New' или 'Создать репозиторий'.\n"
        "4. После создания скопируйте ссылку на репозиторий и вставьте её в поле выше.")
        tip .setWordWrap (True )
        tip .setStyleSheet ("цвет: #ааа; размер шрифта: 13 пикселей;")
        label =QLabel ("Введите данные для GitHub:")
        label .setFont (font )
        layout .addWidget (label )
        layout .addWidget (self .username_input )
        layout .addWidget (self .email_input )
        layout .addWidget (self .repo_input )
        layout .addWidget (self .create_repo_btn )
        layout .addWidget (tip )
        layout .addWidget (self .next_btn )
        layout .addStretch ()
        self .username_input .textChanged .connect (self .check_fields )
        self .email_input .textChanged .connect (self .check_fields )
        self .repo_input .textChanged .connect (self .check_fields )
        self .check_fields ()
        self .stacked .addWidget (w )
    def init_screen2 (self ):
        w =QWidget ()
        layout =QVBoxLayout (w )
        font =QFont ()
        font .setPointSize (16 )
        self .select_folder_btn =QPushButton ("📂 Выбрать папку проекта")
        self .select_folder_btn .setFont (font )
        self .select_folder_btn .setMinimumHeight (40 )
        self .select_folder_btn .clicked .connect (self .select_folder )
        self .files_list =QListWidget ()
        self .files_list .setFont (font )
        self .files_list .setVisible (False )
        files_buttons_layout =QHBoxLayout ()
        self .select_all_btn =QPushButton ("Выбрать все")
        self .select_all_btn .setFont (font )
        self .select_all_btn .setMinimumHeight (40 )
        self .select_all_btn .clicked .connect (self .select_all_files )
        self .select_all_btn .setVisible (False )
        self .clear_selection_btn =QPushButton ("Очистить выбор")
        self .clear_selection_btn .setFont (font )
        self .clear_selection_btn .setMinimumHeight (40 )
        self .clear_selection_btn .clicked .connect (self .clear_selection )
        self .clear_selection_btn .setVisible (False )
        files_buttons_layout .addWidget (self .select_all_btn )
        files_buttons_layout .addWidget (self .clear_selection_btn )
        self .commit_message =QLineEdit ()
        self .commit_message .setPlaceholderText ("Введите комментарий к коммиту")
        self .commit_message .setFont (font )
        buttons_layout =QHBoxLayout ()
        self .back_btn =QPushButton ("Назад")
        self .back_btn .setFont (font )
        self .back_btn .setMinimumHeight (40 )
        self .back_btn .clicked .connect (lambda :self .stacked .setCurrentIndex (0 ))
        self .commit_btn =QPushButton ("🔘 Сделать коммит и push")
        self .commit_btn .setFont (font )
        self .commit_btn .setMinimumHeight (40 )
        self .commit_btn .clicked .connect (self .make_commit )
        self .exit_btn =QPushButton ("Выйти")
        self .exit_btn .setFont (font )
        self .exit_btn .setMinimumHeight (40 )
        self .exit_btn .clicked .connect (self .close )
        buttons_layout .addWidget (self .back_btn )
        buttons_layout .addWidget (self .commit_btn )
        buttons_layout .addWidget (self .exit_btn )
        self .progress_bar =QProgressBar ()
        self .progress_bar .setMinimum (0 )
        self .progress_bar .setMaximum (100 )
        self .progress_bar .setValue (0 )
        self .progress_bar .setTextVisible (True )
        layout .addWidget (self .select_folder_btn )
        layout .addWidget (self .files_list )
        layout .addLayout (files_buttons_layout )
        layout .addWidget (self .commit_message )
        layout .addLayout (buttons_layout )
        layout .addWidget (self .progress_bar )
        self .stacked .addWidget (w )
    def on_next_clicked (self ):
        self .user_data ['username']=self .username_input .text ()
        self .user_data ['email']=self .email_input .text ()
        self .user_data ['repo_url']=self .repo_input .text ()
        self .save_user_data ()
        self .stacked .setCurrentIndex (1 )
    def check_fields (self ):
        if self .username_input .text ()and self .email_input .text ()and self .repo_input .text ():
            self .next_btn .setEnabled (True )
        else :
            self .next_btn .setEnabled (False )
    def open_github_repos (self ):
        username =self .username_input .text ().strip ()
        if username :
            url =f"https://github.com/{username }?tab=repositories"
        else :
            url ="https://github.com/"
        webbrowser .open (url )
    def select_folder (self ):
        folder =QFileDialog .getExistingDirectory (self ,"Выберите папку проекта")
        if folder :
            total_size =0
            for dirpath ,dirnames ,filenames in os .walk (folder ):
                for f in filenames :
                    fp =os .path .join (dirpath ,f )
                    total_size +=os .path .getsize (fp )
            if total_size >100 *1024 *1024 :
                QMessageBox .warning (self ,"Ошибка","Размер папки превышает 100 МБ!")
                return
            self .project_path =folder
            self .select_folder_btn .setText (f"📂 Выбрана папка: {os .path .basename (folder )}")
            self .files_list .clear ()
            self .files_list .setVisible (True )
            self .select_all_btn .setVisible (True )
            self .clear_selection_btn .setVisible (True )
            for root ,dirs ,files in os .walk (folder ):
                for file in files :
                    file_path =os .path .join (root ,file )
                    relative_path =os .path .relpath (file_path ,folder )
                    item =QListWidgetItem ()
                    checkbox =QCheckBox (relative_path )
                    checkbox .setChecked (True )
                    self .files_list .addItem (item )
                    self .files_list .setItemWidget (item ,checkbox )
    def select_all_files (self ):
        for i in range (self .files_list .count ()):
            item =self .files_list .item (i )
            checkbox =self .files_list .itemWidget (item )
            checkbox .setChecked (True )
    def clear_selection (self ):
        for i in range (self .files_list .count ()):
            item =self .files_list .item (i )
            checkbox =self .files_list .itemWidget (item )
            checkbox .setChecked (False )
    def get_selected_files (self ):
        selected_files =[]
        for i in range (self .files_list .count ()):
            item =self .files_list .item (i )
            checkbox =self .files_list .itemWidget (item )
            if checkbox .isChecked ():
                selected_files .append (checkbox .text ())
        return selected_files
    def make_commit (self ):
        if not hasattr (self ,'project_path'):
            QMessageBox .warning (self ,"Ошибка","Сначала выберите папку проекта!")
            return
        selected_files =self .get_selected_files ()
        if not selected_files :
            QMessageBox .warning (self ,"Ошибка","Выберите хотя бы один файл для коммита!")
            return
        commit_message =self .commit_message .text ()
        if not commit_message :
            commit_message ="Обновить проект"
        if not self .check_git_installed ():
            reply =QMessageBox .question (self ,"Git не установлен",
            "Git не установлен на вашем компьютере. Хотите скачать Git?",
            QMessageBox .StandardButton .Yes |QMessageBox .StandardButton .No )
            if reply ==QMessageBox .StandardButton .Yes :
                webbrowser .open ("https://git-scm.com/downloads")
            return
        self .progress_bar .setValue (0 )
        self .commit_btn .setEnabled (False )
        self .worker =GitWorker (
        self .username_input .text (),
        self .email_input .text (),
        self .repo_input .text (),
        self .project_path ,
        commit_message ,
        selected_files
        )
        self .worker .finished .connect (self .on_commit_finished )
        self .worker .start ()
    def on_commit_finished (self ,success ,message ):
        self .commit_btn .setEnabled (True )
        if success :
            self .progress_bar .setValue (100 )
            QMessageBox .information (self ,"Успех",message )
        else :
            QMessageBox .critical (self ,"Ошибка",message )
    def check_git_installed (self ):
        try :
            subprocess .run (["git","--version"],capture_output =True ,check =True )
            return True
        except (subprocess .SubprocessError ,FileNotFoundError ):
            return False
    def install_git (self ):
        reply =QMessageBox .question (self ,"Git не установлен",
        "Git не установлен на вашем компьютере. Хотите установить Git автоматически?",
        QMessageBox .StandardButton .Yes |QMessageBox .StandardButton .No )
        if reply ==QMessageBox .StandardButton .Yes :
            self .installer =GitInstaller ()
            self .installer .finished .connect (self .on_git_installation_finished )
            self .installer .start ()
        else :
            webbrowser .open ("https://git-scm.com/downloads")
            sys .exit ()
    def on_git_installation_finished (self ,success ,message ):
        if success :
            QMessageBox .information (self ,"Успех",message )
            self .load_user_data ()
            self .init_ui ()
        else :
            QMessageBox .critical (self ,"Ошибка",message )
            webbrowser .open ("https://git-scm.com/downloads")
            sys .exit ()
if __name__ =='__main__':
    app =QApplication (sys .argv )
    window =MainWindow ()
    window .show ()
    sys .exit (app .exec ())