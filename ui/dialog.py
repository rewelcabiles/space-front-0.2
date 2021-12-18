import pygame as pg
import pygame_gui
import json

from game.constants import *

with open("data/dialogue.json") as f:
    dialog_data = json.load(f)


        

class DialogTree:
    def __init__(self, uimanager, system) -> None:
        self.visible = False
        self.w = WIDTH
        self.h = HEIGHT

        self.ui_manager = uimanager
        
        self.panels = pygame_gui.elements.UIPanel(
            starting_layer_height=1,
            object_id = "DialogPanels",
            relative_rect = pg.Rect(0, -200, WIDTH, 200),
            manager = self.ui_manager,
            anchors = { "top" : "bottom", "left" : "left", "right" : "right", "bottom" : "bottom"},
            visible=0)
        self.speaker = pygame_gui.elements.UITextBox(
            object_id = "DialogSpeaker",
            container = self.panels,
            html_text = "",
            relative_rect = pg.Rect(0, 0, WIDTH, 40),
            manager = self.ui_manager,
            anchors = { "top" : "top", "left" : "left", "right" : "right", "bottom" : "bottom"})
        self.text_body = pygame_gui.elements.UITextBox(
            object_id = "DialogText",
            container = self.panels,
            html_text = "",
            relative_rect = pg.Rect(0, 40, WIDTH, 150),
            manager = self.ui_manager,
            anchors = { "top" : "top", "left" : "left", "right" : "right", "bottom" : "bottom"})
        #self.goto_id("d5abd9d6-565d-4d29-8254-8011d00f5db7")
        #self.text_body.set_active_effect(pygame_gui.TEXT_EFFECT_TYPING_APPEAR)
 
    def goto_id(self, dialog_id):
        
        if dialog_id == "exit_dialog":
            self.panels.hide()
            return
        dialog_obj = dialog_data[dialog_id]       
        #self.text_body.set_active_effect(pygame_gui.TEXT_EFFECT_TYPING_APPEAR)
        if dialog_obj["type"] == "Text":
            self.speaker.html_text = dialog_obj["actor"]
            self.text_body.html_text = dialog_obj["name"]

        elif dialog_obj["type"] == "Set":
            if dialog_obj["variable"] == "view_shop":
                pass

        if "choices" in dialog_obj.keys():
            self.text_body.html_text += "<br> <br>"
            iterator = 1
            for choice_id in dialog_obj["choices"]:
                choice_obj = dialog_data[choice_id]
                self.text_body.html_text += "<a href='{}'>{}) {}</a><br>".format(choice_obj["next"], iterator, choice_obj["title"])
                iterator += 1
        
        if "next" in dialog_obj.keys():
            if dialog_obj["next"] == None:
                self.text_body.html_text += "<br><br><a href='exit_dialog'>[Click To Exit]</a><br>"
            else:
                self.text_body.html_text += "<br><br><br><a href='{}'>[Click to continue]</a><br>".format(dialog_obj["next"])

        if dialog_obj["type"] == "Set":
            self.goto_id(dialog_obj["next"])

        
        
        self.speaker.rebuild()
        self.text_body.rebuild()
        self.panels.show()




    def resize(self, w, h):
        self.w = w
        self.h = h
        self.panel.set_dimensions((self.w - self.margin * 2, self.h - self.margin * 2))

