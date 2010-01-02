"""
extractor for zip and rar file and a future support file 7-zip.

frost
"""

# Modules general
import os
import sys
from traceback import print_exc

# Modules XBMC
from xbmcgui import DialogProgress
from xbmc import executebuiltin, sleep

# Modules custom
import shutil2


DIALOG_PROGRESS = DialogProgress()


def get_time_sleep( filename ):
    # faut vraiment laisser xbmc le temps d'extraire l'archive environ 1 seconde pour 1 mo
    # plus l'archive est grosse plus cela va etre long
    try:
        slp = int( os.path.getsize( filename ) / 1000 )
    except:
        print_exc()
        slp = 0
    if slp < 1000: slp = 1000
    return slp


def unrar( filename, destination=None, report=False ):
    from rarfile import RarFile
    base_dir = ""
    if destination is None:
        destination = os.path.dirname( filename )
    try:
        rar = RarFile( filename, "r" )
        namelist = rar.namelist()
        total_items = len( namelist ) or 1
        diff = 100.0 / total_items
        percent = 0
        # nom du dossier racine
        root_dir = namelist[ -1 ]
        is_root_dir = True
        # si root_dir n'est pas un dossier ou n'est pas la racine, on se base sur le nom de l'archive
        #print root_dir
        if not rar.getinfo( root_dir ).isdir():
            is_root_dir = False
        else:
            for i in namelist:
                #print root_dir in i, i
                if not root_dir in i:
                    is_root_dir = False
                    break
        if not is_root_dir:#rar.getinfo( root_dir ).isdir():
            root_dir = os.path.basename( os.path.splitext( filename )[ 0 ] )
        base_dir = os.path.join( destination, root_dir )
        if os.path.isdir( base_dir ):
            shutil2.rmtree( base_dir )
        os.makedirs( base_dir )
        time_sleep = get_time_sleep( filename )
        # avec cette methode on extract dans le dossier ou est l'archive
        ok = executebuiltin( 'XBMC.Extract(%s)' % ( filename, ) )
        #sleep une seconde ou plus selon la drosseur du fichier le temps que le builtin est fini car l'action suivante
        # "os.listdir" est excecuter avant la fin du builtin
        sleep( time_sleep )
        # si le dossier base_dir est vide on move les items de namelist dedans
        if not os.listdir( base_dir ):
            for item in namelist:
                src = os.path.normpath( os.path.join( os.path.dirname( filename ), item ) )
                dst = os.path.normpath( os.path.join( base_dir, item ) )
                if not rar.getinfo( item ).isdir():
                    if not os.path.isdir( os.path.dirname( dst ) ):
                        os.makedirs( os.path.dirname( dst ) )
                    shutil2.move( src, dst, overwrite=True )
                elif os.path.exists( src ) and not os.listdir( src ):
                    shutil2.rmtree( src )
        #maintenant on verifier l'extraction d'xbmc avec la liste de la lib rarfile
        if os.path.isdir( base_dir ):
            size = 0
            list_size = 0
            if not root_dir in namelist:
                list_size -= 1
            namelist = [ os.path.split( item )[ 1 ] for item in namelist ]
            for root, dirs, files in os.walk( base_dir, topdown=False ):
                percent += diff
                list_size += 1
                for file in files:
                    percent += diff
                    list_size += 1
                    if report:
                        if DIALOG_PROGRESS.iscanceled():
                            break
                        DIALOG_PROGRESS.update( int( percent ), "Unrar %i of %i items" % ( list_size, total_items ), file, "Please wait..." )
                        #print round( percent, 2 ), file
                    if file in namelist:
                        size += os.path.getsize( os.path.join( root, file ) )
                    else:
                        print "Error %s est dans la liste de depart!" % file
            #print size
            if not size:
                print "Error for extracting rar: %s" % filename
        rar.close()
        del rar
        # si list_size est pas declarer une erreur automatique est creer ;)
        return base_dir, list_size == total_items
    except:
        print_exc()
        return "", False


def unzip( filename, destination=None, report=False ):
    from zipfile import ZipFile
    base_dir = ""
    if destination is None:
        destination = os.path.dirname( filename ) #=> extraction in current directory
    try:
        zip = ZipFile( filename, "r" )
        namelist = zip.namelist()
        total_items = len( namelist ) or 1
        diff = 100.0 / total_items
        percent = 0
        # nom du dossier racine
        root_dir = namelist[ 0 ]
        is_root_dir = True
        # si root_dir n'est pas un dossier ou n'est pas la racine, on se base sur le nom de l'archive
        #print root_dir
        if not root_dir.endswith( "/" ) and ( zip.getinfo( root_dir ).file_size > 0 ):
            is_root_dir = False
        else:
            for i in namelist:
                #print root_dir in i, i
                if not root_dir in i:
                    is_root_dir = False
                    break
        base_dir = os.path.join( destination, root_dir.rstrip( "/" ) )
        if not is_root_dir:#root_dir.endswith( "/" ) and ( zip.getinfo( root_dir ).file_size > 0 ):
            root_dir = os.path.basename( os.path.splitext( filename )[ 0 ] )
            destination = os.path.join( destination, root_dir )
            base_dir = destination
        if os.path.isdir( base_dir ):
            shutil2.rmtree( base_dir )
        os.makedirs( base_dir )
        for count, item in enumerate( namelist ):
            percent += diff
            if report:
                if DIALOG_PROGRESS.iscanceled():
                    break
                DIALOG_PROGRESS.update( int( percent ), "Unzipping %i of %i items" % ( count + 1, total_items ), item, "Please wait..." )
                #print round( percent, 2 ), item
            if not item.endswith( "/" ):
                root, name = os.path.split( item )
                directory = os.path.normpath( os.path.join( destination, root ) )
                if not os.path.isdir( directory ): os.makedirs( directory )
                file( os.path.join( directory, name ), "wb" ).write( zip.read( item ) )
        zip.close()
        del zip
        return base_dir, True
    except:
        print_exc()
        return "", False


def extract( filename, destination=None, report=False ):
    ext = os.path.splitext( filename )[ -1 ]
    if ext == ".zip":
        return unzip( filename, destination, report )
    elif ext == ".rar":
        return unrar( filename, destination, report )
    elif ext == ".7z":
        # test for future support 7-zip archive, not supported for a moment
        # mais il semblerais que le librairie "pylzma" marche bien, http://www.joachim-bauch.de/projects/python/pylzma/
        # reste a compiler cette lib pour xbmc linux, win32/xbox et osx semble pas etre supporter
        # Note faut compiler cette lib avec python 2.4, sinon elle sera pas compatible avec xbmc, pas certain a 100 pour 100.
        #ok = executebuiltin( 'XBMC.Extract(%s)' % ( filename, ) )
        print "L'archive '%s' n'est pas pris en charge..." % os.path.basename( filename )
    return "", False


def copy_dir( dirname, destination, overwrite=True ):
    if not overwrite and os.path.isdir( destination ):
        shutil2.rmtree( destination )
    shutil2.copytree( dirname, destination, overwrite=overwrite )


def copy_inside_dir( dirname, destination, overwrite=True ):
    list_dir = os.listdir( dirname )
    for file in list_dir:
        src = os.path.join( dirname, file )
        dst = os.path.join( destination, file )
        if os.path.isfile( src ):
            if not os.path.isdir( os.path.dirname( dst ) ):
                os.makedirs( os.path.dirname( dst ) )
            if not overwrite and os.path.isfile( dst ):
                os.unlink( dst )
            shutil2.copyfile( src, dst, overwrite=overwrite )
        elif os.path.isdir( src ):
            if not overwrite and os.path.isdir( dst ):
                shutil2.rmtree( dst )
            shutil2.copytree( src, dst, overwrite=overwrite )
