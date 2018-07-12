import os
from Framework.lib.gui_loader import gui_loader
from Framework.lib.ui.qt.QT import QtCore, QtWidgets, QtGui

form, base = gui_loader.load_ui_type(os.path.join(os.path.dirname(__file__), "ui", "anim_prepare_ui.ui"))

import os
from maya import mel
from maya import cmds
import shotgun_api3 as sapi
from Framework.plugins.dependency_uploader.uploader_window import UploaderBackgroundWidget

class Scnforanim(form, base):
    shotSeq = None
    shotNumber = None
    seqName = None
    shotInfo = None
    shot_assets= None
    shot_chars = None
    shot_props = None
    shots = []
    sg = None
    cut_in = None
    cut_out = None
    cam_shake = False
    escenario = None
    
    def __init__(self, parent=None):
        super(Scnforanim, self).__init__(parent)
        self.setupUi(self)
        self.logInShotgun()
        self.shotgunInfo()
        self.connectSignals()


    def connectSignals(self):
        print ("KK")
        self.aceptarButton.clicked.connect(self.publishShot)
        self.sequenceButton.currentIndexChanged.connect(self.refreshShotInfo)
    
    def publishShot (self):
        cmds.file(new=True, f=True)
        self._splitShotName()
        self._importCamera()
        self._importAudio ()
        self._importEscenario ()
        self._importChars ()
        self._importProps ()
        self._renderSetting()
        self._saveShot()
        
        
    def logInShotgun (self):
        self.sg = sapi.Shotgun("https://esdip.shotgunstudio.com",
                                  login="tdevelopment",
                                  password="BM@Developement")
    def shotgunInfo(self):
        self.sequenceButton.clear()
        shots= self.sg.find("Shot", filters=[['project','is', {'type': 'Project','id': 86}]], fields=["code", "sg_status_list"])
        for n in range (0, len(shots)):
            self.sequenceButton.addItem(shots[n]["code"])
            self.shots.append (shots[n]["code"])
        print shots
        
    def refreshShotInfo (self):
        num = self.sequenceButton.currentIndex()
        print num
        self.shotSeq = self.shots[num]
        print self.shotSeq
        self.shotInfo = self.sg.find("Shot", filters=[["code", "is", self.shotSeq],['project','is', {'type': 'Project','id': 86}]], fields=["code", "sg_status_list", "sg_cut_in", "sg_cut_out", "assets", "sg_camera_shake", "sg_escenario"])
        self.cut_in = self.shotInfo[0]["sg_cut_in"]
        self.cut_out = self.shotInfo[0]["sg_cut_out"]
        self.shot_assets= self.shotInfo[0]["assets"]
        self.escenario = self.shotInfo[0]["sg_escenario"]
        self.escenarioButton.setText(str(self.escenario))
        elem= list()
        self.shot_chars = list()
        self.shot_props = list()
        for n in range (0, len(self.shot_assets)):
            elem= self.sg.find('Asset', filters=[['code', "is", self.shot_assets[n]["name"]], ['project','is', {'type': 'Project','id': 86}]], fields=["code","sg_asset_type"])
            if elem[0]["sg_asset_type"] == 'Character':
                self.shot_chars.append(elem[0]["code"])
            elif elem[0]["sg_asset_type"] == 'Prop':
                self.shot_props.append(elem[0]["code"])
        self.charsButton.setText(str(self.shot_chars))
        self.propsButton.setText(str(self.shot_props))
        print elem
        self.cutInButton.setText(str(self.cut_in))
        self.cutOutButton.setText(str(self.cut_out))
        if self.shotInfo[0]["sg_camera_shake"] == True:
            self.cam_shake = True
            self.handicamButton.setDown(True)
        
        
    def _splitShotName (self):
        shotPartsList= []
        shot = self.shotSeq
        print self.shotSeq
        shotPartsList = self.shotSeq.split(".")
        self.shotNumber = shotPartsList[0]
        self.seqName = shotPartsList[1]
        print "plano numero {} y secuencia {}".format( self.shotNumber, self.seqName)
        
    def _importCamera (self):
    
        camera_path = "P:/BM2/seq/{0}/sho/{1}/camera/out/bm2_shocam_seq_{0}_sho_{1}_camera_default_none_out.ma".format(self.shotNumber, self.seqName)
        self._downloadFromDropbox(camera_path)
        cmds.file( camera_path, reference=True, namespace=":")
        
    def _importAudio (self):
        audio_path = "P:/BM2/seq/{0}/sho/{1}/audio/out/bm2_shoaud_seq_{0}_sho_{1}_audio_default_none_out.wav".format(self.shotNumber, self.seqName)
        self._downloadFromDropbox(audio_path)
        node = cmds.file( audio_path, reference=True)
        node = cmds.referenceQuery(node, n=True)
        cmds.setAttr ("{}.offset".format(node[0]), 76)
        cmds.playbackOptions (minTime=self.cut_in, animationStartTime=(self.cut_in-25), maxTime=self.cut_out, animationEndTime=(self.cut_out+25) )
        
    def _importEscenario (self):
        escenarioList = []
        escenarioList = self.escenario.split("_")
        location = escenarioList[0]
        sublocation = escenarioList[1]
        location_path = "P:/BM2/loc/{0}/scn/animPrep/main/out/bm2_locscn_loc_{0}_scn_animPrep_main_{1}_none_out.ma".format(location, sublocation)
        self._downloadFromDropbox(location_path)
        node = cmds.file( location_path, reference=True, namespace=":")
    
    def _importChars (self):
        print self.shot_chars
        for n in range (0, len(self.shot_chars)):
            #P:/BM2/chr/gato/out/rigging/thinhigh/out/bm2_chrout_chr_gato_out_rigging_thinhigh_default_none_out.ma
            #P:/BM2/chr/mortando/out/rigging/thinhigh/out/bm2_chrout_chr_mortando_out_rigging_thinhigh_default_scene_out.ma
            char = self.shot_chars[n]
            char_path = "P:/bm2/chr/{0}/out/rigging/thinhigh/out/bm2_chrout_chr_{0}_out_rigging_thinhigh_default_none_out.ma".format(char)
            self._downloadFromDropbox(char_path)
            node = cmds.file( char_path, reference=True, namespace=self.shot_chars[n])
    '''       
    def _importAlembics (self):
        list_abc=self.shot_props + self.shot_chars
        for n in range (0, len(list_abc)):
            #P:/BM2/seq/pmp/sho/020/previs/out/bm2_shopre_seq_pmp_sho_020_animation_gato_alembic_out.abc
            abc = list_abc[n]
            abc_path = "P:/bm2/seq/{0}/sho/{1}/previs/out/bm2_shopre_seq_{0}_sho_{1}_animation_{2}_alembic_out.abc".format(self.shotNumber, self.seqName, abc)
            print abc_path
            self._downloadFromDropbox(abc_path)
            node = cmds.AbcImport (abc_path, m="import" )'''
            
    def _importProps (self):
        print self.shot_props
        for n in range (0, len(self.shot_props)):
            #P:/BM2/elm/pompero/out/rigging/high/out/bm2_elmout_elm_pompero_out_rigging_high_default_scene_out.ma
            prop = self.shot_props[n]
            prop_path = "P:/bm2/elm/{0}/out/rigging/high/out/bm2_elmout_elm_{0}_out_rigging_high_default_none_out.ma".format(prop)
            self._downloadFromDropbox(prop_path)
            node = cmds.file(prop_path, reference=True, namespace=self.shot_props[n])
            
    def _renderSetting (self):
        if self.cam_shake == False:
            cmds.setAttr ("defaultResolution.width", 1920)
            cmds.setAttr ("defaultResolution.height", 1080)
        elif self.cam_shake == True:
            cmds.setAttr ("defaultResolution.width", 3424)
            cmds.setAttr ("defaultResolution.height", 2202)
            
    def _saveShot (self):
        #P:/BM2/seq/[seqName]/sho/[shotNumber]/scncmp/out/bm2_seqscn_seq_[seqName]_sho_[shotNumber]_scncmp_animprep_scene_out.ma
        
        directory = ( "P:/BM2/seq/{0}/sho/{1}/scncmp/out/".format(self.shotNumber, self.seqName))
        try:
            os.makedirs(directory)
        except:
            pass    
        file_path_list=[]
        file_path_list.append( "P:/BM2/seq/{0}/sho/{1}/scncmp/out/bm2_shoscn_seq_{0}_sho_{1}_scncmp_animprep_scene_out.ma".format(self.shotNumber, self.seqName))
        listNodes = cmds.ls(type = 'unknown')
        cmds.delete(listNodes)
        cmds.file( rename=file_path_list[0] )
        cmds.file (save=True, type='mayaAscii', f=True)   
        self._sendToDropbox(file_path_list, 1)
        
        #P:/BM2/seq/[seqName]/sho/[shotNumber]/animation/wip/bm2_[seqName][shotNumber]_seq_[seqName]_sho_[shotNumber]_animation_animprep_scene_wip.0000.ma
        
        directory = ( "P:/BM2/seq/{0}/sho/{1}/animation/wip/".format(self.shotNumber, self.seqName))
        try:
            os.makedirs(directory)
        except:
            pass  
            
        file_path_list=[]
        file_path_list.append( "P:/BM2/seq/{0}/sho/{1}/animation/wip/bm2_shoani_seq_{0}_sho_{1}_animation_animprep_scene_wip.0001.ma".format(self.shotNumber, self.seqName))
        

        cmds.file( rename=file_path_list[0] )
        cmds.file (save=True, type='mayaAscii', f=True)
        self._sendToDropbox(file_path_list, 1)
        
    def _sendToDropbox(self, file_path_list, max_threads):
        uploader_background_widget = UploaderBackgroundWidget(file_path_list=file_path_list, max_threads=max_threads)
        x = uploader_background_widget.execute_upload_process()
        print x
        
    def _downloadFromDropbox (self, path):
        from Framework.plugins.dependency_loader.downloader import Downloader, DownloaderResponse
        from Framework.lib.ui.qt.QT import QtCore, QtWidgets, QtGui
        
        if os.path.isfile(path) == True:
            print "estamos dentro del if del path" + path
            print os.path.isfile(path)
        else:
            self.download_finished = False
            downloader = Downloader()
            file_list = []
            file_list.append(path)
            print file_list
            downloader.set_files_to_process(file_list)
            downloader.set_maxium_threads(1)
            downloader.on_finish_download.connect(self.on_download_finished, QtCore.Qt.QueuedConnection)
            downloader.start_download_process()

            while self.download_finished  == False:            
                if os.path.isfile(path) == False:
                    import time
                    time.sleep(10)
                    print "Downloading {}....".format(path)
                    if self.download_finished:
                        break
                    self.download_finished  = False
                elif os.path.isfile(path) == True: 
                    break

    def on_download_finished(self):
          self.download_finished  = True
          print self.download_finished, "TERMINA JODER "       