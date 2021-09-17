import tkinter as tk
import os
from Biometric_params import *
from center import center
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from RecordingFile import *
import shutil
from LiveMicWidget import *
from bio_params_view import *
from pydub import AudioSegment, effects
import time
import RightMainForm

class NetTrain:
    def __init__(self, train_list):
        global btn_record_image
        btn_record_image = tk.PhotoImage(file=os.getcwd() + "\\res\\record.png")
        global voice_params_image
        voice_params_image = tk.PhotoImage(file=os.getcwd() + "\\res\\bio_params.png")
        global key_image
        key_image = tk.PhotoImage(file=os.getcwd() + "\\res\\key_image.png")
        global btn_train_image
        btn_train_image = tk.PhotoImage(file=os.getcwd() +"\\res\\neuron.png")
        self.mylist = train_list

    def load_data(self,file):
        output_l = []
        for line in file:
            for x in line.split():
                output_l.append(float(x))
        output = np.array(output_l)
        if len(output_l) / 194 > 1:
            output.shape = (int(len(output_l) / 194), 194)
        return output

    def get_container(self):
        f_mat = open(os.getcwd() + '\\Alien\\mat_og_all_aliences.txt', 'r')
        f_std = open(os.getcwd() + '\\Alien\\std_all_aliences.txt', 'r')
        self.mat_og_aliences = self.load_data(f_mat)
        self.std_aliences = self.load_data(f_std)

    def buttonClickedTrain(self):
        self.newWindow = tk.Toplevel()
        self.newWindow.title("User Identification")
        self.newWindow.focus_set()
        self.newWindow.minsize(width=1050, height=800)
        leftform = tk.Frame(master=self.newWindow, bd=2, width=800, height=80, relief=tk.GROOVE)
        leftform.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Identification results
        rightform = tk.Frame(master=self.newWindow, bd=2, width=250, height=800, relief=tk.SUNKEN)
        rightform.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.button1_was_clicked = False
        self.recording_started = False
        self.recording_stopped = False
        self.get_container()
        self.Bioview = get_bio_params_view()
        self.porog, self.all_svoi, self.mat_og_svoi, self.std_svoi = self.Bioview.get_porog()


        LiveMicWidget(master=leftform)

        self.btn_start = tk.Button(master=leftform, text="Identification", bg="green",font="85",
                                   image=btn_record_image,
                                   compound=tk.LEFT, command=self.buttonClickedRecord)

        self.btn_start.pack(side=tk.BOTTOM)


        self.btn_get_bio_params = tk.Button(master=rightform, text="Biometric \n parameters",
                                            image=voice_params_image, bg="medium aquamarine",
                                            command=self.Bioview.buttonClickedGetBio,
                                            font="18", compound=tk.LEFT)
        self.btn_get_bio_params.pack(pady=50)


        self.btn_additional_training  = tk.Button(master=rightform, text="Additional training ",
                                     image = btn_train_image,
                                     bg="medium aquamarine",
                                     command=self.additional_training,
                                     font="18", compound=tk.LEFT)
        self.btn_additional_training.pack(pady=40)

        self.newWindow.protocol('WM_DELETE_WINDOW', self.exit)
        self.save_container()
        center(self.newWindow)

    #Additional training, add an image to the container
    def additional_training(self):
        self.get_new_svoi()
        self.save_container()
        self.refresh_training_base()
        tk.messagebox.showinfo(title="Additional training ", message="Additional training completed ")

    def rename_all(self, path):
        vart = "Images\HuyPizdaDjigurda №"
        filelist = [f for f in os.listdir(path)]
        start = 1
        self.mylist.delete(0, self.mylist.size())
        for f in filelist:
            if f.endswith(".wav"):
                os.rename("Images \\" + f, vart + str(start) + ".wav")
                start += 1

    def refresh_training_base(self):
        self.rename_all("Images")
        start = 1
        filelist_new = [f2 for f2 in os.listdir("Images")]
        for f2 in filelist_new:
            if f2.endswith(".wav"):
                os.rename("Images\\" + f2, "Images\Image №" + str(start) + ".wav")
                index = f2.rfind("/") + 1
                self.mylist.insert(tk.END, "Image №" + str(start))
                start += 1

    #overwrite the "Own" parameters
    def get_new_svoi(self):
        users_bio_params = self.Bioview.get_bio_params(os.getcwd() + "\Testing\\")
        size = len(users_bio_params)
        images = []
        for zxc in range(len(users_bio_params)):
            len_bio_params = 0
            for qwe in range(len(users_bio_params[zxc])):
                signal = users_bio_params[zxc][qwe]
                for parametr in signal:
                    images.append(float(parametr))
                len_bio_params += len(signal)
        new_svoi_t = np.array(images)
        new_svoi_t.shape = (size, len_bio_params)
        self.new_svoi = self.norm(new_svoi_t)
        new_all_svoi = []
        for zxc in range(len(self.all_svoi)):
            for qwe in range(len(self.all_svoi[zxc])):
                new_all_svoi.append(self.all_svoi[zxc][qwe])
        for new_one in range(len(self.new_svoi)):
            new_all_svoi.append(self.new_svoi[new_one])
        new_svoi_t = np.array(new_all_svoi)
        new_svoi_t.shape = (len(self.all_svoi) + 1, len_bio_params-1)
        self.all_svoi = new_svoi_t
        self.mat_og_svoi = np.mean(self.all_svoi, axis=0)
        self.std_svoi = np.std(self.all_svoi, axis=0)

    #save bio-parameters container
    def save_container(self):
        fwrite = open('Testing\\svoi.txt', 'w')
        for zxc in range(len(self.all_svoi)):
            for asd in range(len(self.all_svoi[zxc])):
                fwrite.write(str(self.all_svoi[zxc][asd]) + "\t")
            fwrite.write("\n")

        fwrite2 = open('Testing\\mat_svoi.txt', 'w')
        for zxc in range(len(self.mat_og_svoi)):
            fwrite2.write(str(self.mat_og_svoi[zxc]) + "\t")

        fwrite3 = open('Testing\\std_svoi.txt', 'w')
        for zxc in range(len(self.std_svoi)):
            fwrite3.write(str(self.std_svoi[zxc]) + "\t")


    def exit(self):
        if os.path.exists(os.getcwd() + "\Images\\" + "Image_for_testing" + ".wav"):
            os.remove(os.getcwd() + "\Images\\" + "Image_for_testing" + ".wav")
        self.newWindow.destroy()

    #Normalize relative to the base "all ALLIENCES"
    def norm(self, images):
        norm_im = []
        for qwe in range(len(images)):
            for asd in range(len(self.mat_og_aliences) - 1):
                normed = (images[qwe][asd] - self.mat_og_aliences[asd]) / self.std_aliences[asd]
                norm_im.append(normed)
        output = np.array(norm_im)
        if len(norm_im) / 193 > 1:
            output.shape = (int(len(norm_im) / 193), 193)
        return output

    #Calculate the distance between the test pattern and the expected value of the training sample
    def calculate_threshold(self):
        sample_for_test = os.getcwd() + "\Testing\Image_for_testing.wav"
        self.gottenparams = self.Bioview.get_bio_params(os.getcwd() + "\Testing")
        images = []
        size = len(self.gottenparams)
        images = []
        len_bio_params = 0
        for zxc in range(len(self.gottenparams)):
            len_bio_params = 0
            for qwe in range(len(self.gottenparams[zxc])):
                signal = self.gottenparams[zxc][qwe]
                for parametr in signal:
                    images.append(float(parametr))
                len_bio_params += len(signal)
        all_enemies_t = np.array(images)
        all_enemies_t.shape = (size, len_bio_params)
        self.all_enemies = self.norm(all_enemies_t)
        dist = 0
        self.until = 193


        for qwe in range(self.until):
            dist += ((self.all_enemies[qwe] - self.mat_og_svoi[qwe]) ** 2) / (self.std_svoi[qwe] ** 2)

        self.all_dist = math.sqrt(dist)
        print("difference  = ", self.all_dist)
        self.svoi_a = True
        if self.all_dist >= self.porog:
            print("ALLIEN")
            self.svoi_a = False
        if self.svoi_a:
            print("OWN")

    def match_target_amplitude(self, sound, target_dBFS):
        change_in_dBFS = target_dBFS - sound.dBFS
        return sound.apply_gain(change_in_dBFS)

    def buttonClickedRecord(self):
        was_start = False
        if self.btn_start["text"] == "Identification" and not self.recording_started:
            print("writing an image for Identification")
            self.recording_file = RecordingFile(fname = os.getcwd() + "\Testing\\"+ "Image_for_testing.wav",
                                                mode='wb',
                                                channels=1,
                                                rate=16000,
                                                frames_per_buffer=1024)
            self.recording_file.start_recording()
            self.recording_started = True
            self.button1_was_clicked = True
            self.btn_start.config(text="Stop recording")
            self.btn_start.config(bg = "red")
            was_start = True

        if  self.btn_start["text"] == "Stop recording" and self.recording_started and not was_start:
            self.recording_file.stop_recording()
            self.recording_started = False
            self.recording_stopped = True
            print("finished recording ")
            sound = AudioSegment.from_file(os.getcwd() + "\Testing\\"+ "Image_for_testing.wav", "wav")
            normalized_sound = self.match_target_amplitude(sound, -20.0)
            normalized_sound.export(os.getcwd() + "\\Testing\\"+ "Image_for_testing.wav", format="wav")


            current_max_number = 0
            current_test_sbor = "Image_for_testing №1.wav"
            for f in os.listdir(os.getcwd() + "\\Testing\\Any collection"):
                if f.endswith('.wav'):
                    index = f.find("№") + 1
                    if current_max_number < int(f[index:-4]):
                        current_max_number = int(f[index:-4])
                        current_test_sbor = "Image_for_testing №" + str(current_max_number) + ".wav"
            shutil.copy2(os.getcwd() + "\Testing\Image_for_testing.wav", os.getcwd() + "\Testing\Any collection")
            os.rename(os.getcwd() + "\Testing\Any collection\Image_for_testing.wav", os.getcwd() + "\Testing\Any collection\\" + "Image_for_testing №" + str(current_max_number + 1) + ".wav")
            self.calculate_threshold()

            if self.svoi_a:
                tk.messagebox.showinfo(title="User Identification", message = "Access is allowed\n"
                    + "\nDistance:\n" + str(self.all_dist) + "\nMaximum threshold: " + str(self.porog))
            else:
                tk.messagebox.showerror(title="User Identification", message = "Access is denied\n"
                    + "\nDistance:\n" + str(self.all_dist) + "\nMaximum threshold: " + str(self.porog))
            self.newWindow.focus_set()
            shutil.copy2(os.getcwd() + "\Testing\\"+ "Image_for_testing.wav",os.getcwd() + "\Images")
            self.btn_start.config(text="Identification")
            self.btn_start.config(bg="green")

            #Output to txt add-on
            file_dist = open(os.getcwd() + "\Testing\distances.txt", 'a')
            file_dist.write("Distance = " + str(self.all_dist) + "\n")