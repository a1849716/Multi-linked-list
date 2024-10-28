# Multi-linked-list

This is an implementation of Multi-Linked-List.
To start the program, run the command:

```bash
python3 assignment3.py -l (port_number) -p "search pattern"
```

This will start the server, then to send a file over a netcat command can be used:

```bash
nc localhost (port_number) < "file name"
```

every 5 seconds, a paragraph will be printed with what search pattern is being looked at and the frequency of each of the books. The book names are the books in order and the book_id that gets incremented each time.