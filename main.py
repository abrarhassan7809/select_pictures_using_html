import os
from fastapi import FastAPI, UploadFile, File, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from starlette.requests import Request
from starlette.responses import RedirectResponse

IMAGEDIR = 'static/'

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/show_images/")
async def show_images(request: Request):
    result = []
    if os.listdir(IMAGEDIR):
        if len(os.listdir(IMAGEDIR)) >= 0:
            for file_name in os.listdir(IMAGEDIR):
                if file_name.endswith(('.jpg', '.jpeg', '.png')):
                    file_path = os.path.join(IMAGEDIR, file_name)
                    result.append(os.path.abspath(file_path))
                else:
                    return 'Invalid picture format'
        else:
            return 'Empty'
    return templates.TemplateResponse("index_images.html", {"request": request, "result": result})


@app.post('/upload_files/')
async def upload_files(file: UploadFile = File(...)):
    errors = []
    contents = await file.read()

    # save the file
    file_path = os.path.join(IMAGEDIR, file.filename)
    if not os.path.exists(file_path):
        with open(file_path, "wb") as f:
            f.write(contents)
        print('Image added successfully')
    else:
        print('Image already exists')

    redirect_url = app.url_path_for('show_images')
    return RedirectResponse(url=redirect_url, status_code=status.HTTP_303_SEE_OTHER)


@app.delete('/delete_image/{image_path}')
async def delete_image(image_path: str):
    file_path = os.path.join(IMAGEDIR, os.path.basename(image_path))
    if os.path.exists(file_path):
        os.remove(file_path)
        print('Image deleted successfully')
    else:
        print('Image not found')

    redirect_url = app.url_path_for('show_images')
    return RedirectResponse(url=redirect_url, status_code=status.HTTP_303_SEE_OTHER)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
