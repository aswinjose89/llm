


import google.generativeai as genai

# Used to securely store your API key
# from google.colab import userdata


GOOGLE_API_KEY="AIzaSyCmev--iPOAVg3QazJEIMrn6zMyG2eFvGI"

genai.configure(api_key=GOOGLE_API_KEY)


for m in genai.list_models():
  if 'generateContent' in m.supported_generation_methods:
    print(m.name)

model = genai.GenerativeModel('gemini-pro')

instruction=  """
The assessment has identified critical vulnerabilities that require immediate attention 
to prevent potential security breaches and data loss

Given Vulnerable source code snippet is
`
<form action="upload_picture.php" method="post" enctype="multipart/form-data">

Choose a file to upload:
<input type="file" name="filename"/>
<br/>
<input type="submit" name="submit" value="Submit"/>

</form>



// Define the target location where the picture being

// uploaded is going to be saved.
$target = "pictures/" . basename($_FILES['uploadedfile']['name']);

// Move the uploaded file to the new location.
if(move_uploaded_file($_FILES['uploadedfile']['tmp_name'], $target))
{
echo "The picture has been successfully uploaded.";
}
else
{
echo "There was an error uploading the picture, please try again.";
}

`

Reply the answer in JSON form with associated properties are programming_language, compiler_name, fixed_source_code, executive_summary, vulnerability_details, vulnerability_type, cwe, cvss_score, nvd

"""
response = model.generate_content(instruction)

# print(response.prompt_feedback)
print(response.text)


