import ftplib, os
import ConfigParser
import zipfile
import xbmc
import xbmcgui
import string
import sys
import traceback

print "****************************************************************"
print "                      Mise  a jour du script                   "
print "****************************************************************"


def zipextraction (archive,pathdst):
    idracine = False
    zfile = zipfile.ZipFile(archive, 'r')
    compteurdossier = 0
    compteurfichier = 0
    for i in zfile.namelist():  ## On parcourt l'ensemble des fichiers de l'archive
        if idracine == False:
            filedst = pathdst + os.sep + i
        else:
            filedtst = pathdst + os.sep + i[len(root):]

        print filedst

        if i.endswith('/'): 
            #Creation des repertoires avant extraction
            compteurdossier = compteurdossier + 1

            if compteurdossier == 1 and compteurfichier == 0:
            #On determine le repertoire racine s'il existe pour le retirer du chemin d'extraction
                idracine = True
                root = i

            else:
                try:
                    os.makedirs(filedtst)
                except Exception, e:
                    print "Erreur creation dossier de l'archive = ",e

        else:
            #Extraction des fichiers
            compteurfichier = compteurfichier + 1
            data = zfile.read(i)                   ## lecture du fichier compresse
            fp = open(filedtst, "wb")  ## creation en local du nouveau fichier
            fp.write(data)                         ## ajout des donnees du fichier compresse dans le fichier local
            fp.close()
    zfile.close()


def start():
    try:
        rootdir = os.path.dirname(os.getcwd().replace(';',''))
        curdir = os.path.join(rootdir, "cache")
    
        confmaj = os.path.join(curdir, "confmaj.cfg")
        config = ConfigParser.ConfigParser()
        config.read(confmaj)
    
        passiondir  = config.get('Localparam', 'passiondir')
        installDir  = config.get('Localparam', 'scriptDir')
        archive     = config.get('Localparam', 'Archive')
        script      = config.get('Localparam', 'Scripttolaunch')       

        sys.path.append(passiondir)
    
        dp = xbmcgui.DialogProgress()
        dp.create("Mise a jour","Mise a jour du script","Veuillez patienter...")
        zipextraction(archive,passiondir)
        dp.close()
        del config #On supprime le config parser
        
        #import CONF
        #CONF.SetConfiguration()
        #dp.close()
    
        
        #import INSTALLEUR
        #INSTALLEUR.start()
        #exec("import " + script)
        print "Lancement du script %s"%script
        #xbmc.executebuiltin('XBMC.RunScript(%s)'%script)
        xbmc.executescript(script)
        print "Sortie de INSTALLMAJ2"
        #sys.exit(0)
    except Exception, e:
        print "INSTALLMAJ : start(): Exception",e
        #dialogError = xbmcgui.Dialog()
        #dialogError.ok("Erreur", "Exception durant l'initialisation")
        print ("error/INSTALLMAJ start: " + str(sys.exc_info()[0]))
        traceback.print_exc()

if __name__ == "__main__":
    #ici on pourrait faire des action si le script �tait lanc� en tant que programme
    print "demarrage du script en tant que programme"
    start()
else:
    #ici on est en mode librairie import�e depuis un programme
    pass

