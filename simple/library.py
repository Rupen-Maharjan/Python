# A simple book adding method to add or remove books to library from library

class library:
    def __init__(self):
        self._num=0
        self._books=[]

    @property
    def check(self):
        lenB=len(self._books)
        if not lenB ==self._num:
            print(f'Numbers dont match len= {lenB} num = {self._num}')
        else:
            print(f'everything is ok\n{self._books}')

    def add(self,*books):

        for book in books:
            self._books.append(book)
            self._num+=1
            print(f'{book} added to library')

    def delete(self,*books):
        for book in books:
            self._books.remove(book)
            self._num-=1
            print(f'{book} removed from library')

lib1= library()
lib1.add('hacker', 'Ai', 'Hacker','Master ai')
lib1.check

lib1.delete('Hacker')
lib1.check
