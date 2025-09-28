# How the image generation works?
refer to this flow:  https://drive.google.com/file/d/1hW3yEeM5DpvwQmuXlTeUSz6Swl356o-m/view?usp=drive_link

# Prerequisites
- download ComfyUI https://www.comfy.org/download
- download dreamshaper model ver 7 https://civitai.com/models/4384?modelVersionId=109123
- put the model under `ComfyUI/models/checkpoints`
- starts ComfyUI server, make sure it is running at port 8080, if default not 8080, run it from terminal, switch to port 8080
    ```bash
    cd /path/to/ComfyUI
    python main.py --port 8080
    ```
- refer to backend/README.md, start the django server

# How to test it?
```bash
cd backend # test run under backend/
python manage.py render_demo --year 2035 # if success, gives rel_path of all four images
python manage.py display_demo --session 1 --turn 1 --option C # if success, can access the image_url (tho it can be none)
```