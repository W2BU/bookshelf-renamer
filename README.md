# bookshelf-renamer
Provides consistent naming for bookshelf folder of different ebook types.

# Features
* FB2, EPUB, PDF support
* Consistent naming with no missing fields
* Easy to expand with other file formats
* Validates and cleans extracted metadata before renaming
* Changes preview
* Add folders to ignore
* Flexible filename string template
* Renaming failures are logged with datailed error explanation

# How to use
Create *FileRenamer* class instance and provide path to folder with books. Call *run* to rename files.

```python
dir = r'C:\Users\user\Books'
fr = FileRenamer(library_directory=dir)
fr.run()
```
To preview built filenames, add *suggest_names = True* in *FileRenamer* constructor. Suggested filenames will be printed in console.

```python
fr = FileRenamer(suggest_names=True)
```

# Demonstration
Filenames suggestions and errors

<img width="849" alt="WindowsTerminal_miXdHiZKnf" src="https://github.com/user-attachments/assets/dc637dea-77f0-4c5e-aa9d-8be4fdb61ad7">