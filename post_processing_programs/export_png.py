import os
import sys

def export_csv(argument_vector):
    try:
        jobname = argument_vector[1]
    except:
        pass
    

    current_working_directory = os.getcwd()
    print(current_working_directory)

    with open("SessionFileShowAndExportPost.ofs", 'w') as session_file_export:
        session_file_export.write(
        f"""
        mode(Post)
        file.open.apply("{current_working_directory}/{jobname}.erg/header.bin", format="OFSolv/Results", variables=Recommended, increments=Recommended, curves=OnDemand)
        hide(items="process(1):Blankholder,Die,Punch")
        view.multiView.set(views="4 Views")
        view.multiView.setActive(views=nextView)
        setVariable("Scalar:Formability", view="3D View 2")
        flcCreateKeeler(materialName="Keeler 1", thickness="0.8", n="0.2", r=1)
        flcAddItem(flc="Keeler 1", item="process(1):Blank")
        view.multiView.setActive(views=nextView)
        setVariable("Scalar:No Variable", view="3D View 3")
        view.multiView.setActive(views=nextView)
        setProcessActive(process=1, view="3D View 4", active=false)
        showMin()
        showMax()
        takeSnapshot("3D View", filename="{current_working_directory}/{jobname}.png", format=Png, drawLogo=Off, drawBorder=Off)
        quit()
        """)
    
    try:
        os.system(f"ofd -s SessionFileShowAndExportPost.ofs -b")
    except:
        print("Export did not work.")

instruction = sys.argv
export_csv(instruction)