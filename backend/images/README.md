# How the image generation works?
refer to this flow:  https://drive.google.com/file/d/1hW3yEeM5DpvwQmuXlTeUSz6Swl356o-m/view?usp=drive_link

# Prerequisites
- download ComfyUI https://www.comfy.org/download
- download dreamshaper model ver 7 https://civitai.com/models/4384?modelVersionId=109123
- put the model under `ComfyUI/models/checkpoints`
- start the ComfyUI server, make sure it is running at port 8000, if default not 8000, run it from terminal, switch to port 8000
    ```bash
    cd /path/to/ComfyUI
    python main.py --port 8000
    ```
- refer to `README.md` and complete the setup instructions there, including starting the Django server

# How to test it?
```bash
cd backend # test run under backend/
python manage.py render_demo --year 2035 # if success, gives rel_path of both images
python manage.py display_demo --session 1 --turn 1 --option C # if success, can access the image_url (tho it can be none)
```