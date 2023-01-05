# Mnemosyne

A simple Python spaced-repetition flashcard app for easily memorizing, learning, or studying anything you like.

## Dependencies

This app relies on the `PyQt6==6.4.0`. If you are missing this library, it can be installed via `pip`:
```
pip install PyQt6
```

## How to use

To open the application, simply run the following in the terminal:
```
python main.py
```

## Decks

Decks are stored in `decks/` as `JSON` files. For example, the `JSON` file for an Italian vocabulary deck looks like this:
```
{
    "srs_method": "Fibonacci",
    "flashcards": [
        {
            "front": "salve",
            "back": "hello (formal)",
            "last_review": "2023-01-04 21:32:26.923312",
            "mem_level": 0
        },
        
        ...
        
    ]
}
```
Further example decks can be found in `example_decks/`.

## Spaced repetition

When creating a deck, you will be prompted to choose a spaced repetition method. As more methods are added, this section will be updated with their respective details.
* **Fibonacci**: expanding intervals between repetitions of flashcard items corresponding to the number of days since the last review according to the Fibonacci sequence
  * The second repetition occurs 1 day after the first, the third one 1 day after the second, the fourth 2 days after the third, the fifth 3 days after the fourth, the sixth 5 days after the fifth, and so on.
