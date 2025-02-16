from fastapi import UploadFile, File

async def provide_prediction_test(file: UploadFile = File(...)):
    # store file
    newFile = file.file.read()
    with open(f"src/storage/input-upload/{file.filename}", "wb") as f:
        f.write(newFile)
    return {"message": "file uploaded","filename":file.filename}