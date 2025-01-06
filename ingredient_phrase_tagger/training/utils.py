import re

from ingredient_phrase_tagger.training import tokenizer


def joinLine(columns):
    return "\t".join(columns)


def cleanUnicodeFractions(s):
    """
    Replace unicode fractions with ascii representation, preceded by a
    space.

    "1\x215e" => "1 7/8"
    """

    fractions = {
        '\x215b': '1/8',
        '\x215c': '3/8',
        '\x215d': '5/8',
        '\x215e': '7/8',
        '\x2159': '1/6',
        '\x215a': '5/6',
        '\x2155': '1/5',
        '\x2156': '2/5',
        '\x2157': '3/5',
        '\x2158': '4/5',
        '\xbc': ' 1/4',
        '\xbe': '3/4',
        '\x2153': '1/3',
        '\x2154': '2/3',
        '\xbd': '1/2',
    }

    for f_unicode, f_ascii in fractions.items():
        s = s.replace(f_unicode, ' ' + f_ascii)

    return s


def unclump(s):
    """
    Replacess $'s with spaces. The reverse of clumpFractions.
    """
    return re.sub(r'\$', " ", s)


def normalizeToken(s):
    """
    ToDo: FIX THIS. We used to use the pattern.en package to singularize words, but
    in the name of simple deployments, we took it out. We should fix this at some
    point.
    """
    return singularize(s)


def getFeatures(token, index, tokens):
    """
    Returns a list of features for a given token.
    """
    length = len(tokens)

    return [("I%s" % index), ("L%s" % lengthGroup(length)),
            ("Yes" if isCapitalized(token) else "No") + "CAP",
            ("Yes" if insideParenthesis(token, tokens) else "No") + "PAREN"]


def singularize(word):
    """
    A poor replacement for the pattern.en singularize function, but ok for now.
    """

    units = {
        "cups": "cup",
        "tablespoons": "tablespoon",
        "teaspoons": "teaspoon",
        "pounds": "pound",
        "ounces": "ounce",
        "cloves": "clove",
        "sprigs": "sprig",
        "pinches": "pinch",
        "bunches": "bunch",
        "slices": "slice",
        "grams": "gram",
        "heads": "head",
        "quarts": "quart",
        "stalks": "stalk",
        "pints": "pint",
        "pieces": "piece",
        "sticks": "stick",
        "dashes": "dash",
        "fillets": "fillet",
        "cans": "can",
        "ears": "ear",
        "packages": "package",
        "strips": "strip",
        "bulbs": "bulb",
        "bottles": "bottle"
    }

    if word in units.keys():
        return units[word]
    else:
        return word


def isCapitalized(token):
    """
    Returns true if a given token starts with a capital letter.
    """
    return re.match(r'^[A-Z]', token) is not None


def lengthGroup(actualLength):
    """
    Buckets the length of the ingredient into 6 buckets.
    """
    for n in [4, 8, 12, 16, 20]:
        if actualLength < n:
            return str(n)

    return "X"


def insideParenthesis(token, tokens):
    """
    Returns true if the word is inside parenthesis in the phrase.
    """
    if token in ['(', ')']:
        return True
    else:
        line = " ".join(tokens)
        return re.match(r'.*\(.*' + re.escape(token) + '.*\).*',
                        line) is not None


def displayIngredient(ingredient):
    """
    Format a list of (tag, [tokens]) tuples as an HTML string for display.

        displayIngredient([("qty", ["1"]), ("name", ["cat", "pie"])])
        # => <span class='qty'>1</span> <span class='name'>cat pie</span>
    """

    return "".join([
        "<span class='%s'>%s</span>" % (tag, " ".join(tokens))
        for tag, tokens in ingredient
    ])


# HACK: fix this
def smartJoin(words):
    """
    Joins list of words with spaces, but is smart about not adding spaces
    before commas.
    """

    input = " ".join(words)

    # replace " , " with ", "
    input = input.replace(" , ", ", ")

    # replace " ( " with " ("
    input = input.replace("( ", "(")

    # replace " ) " with ") "
    input = input.replace(" )", ")")

    return input


def import_data(lines):
    """
    Parse CRF++ output format into structured ingredient data.
    
    Args:
        lines (list): List of strings in CRF++ output format
            
    Returns:
        dict: Dictionary containing parsed ingredient with quantity, unit, name,
              input string, and accuracy scores as a dictionary with 3 decimal places
    """
    ingredient = {
        "qty": "",
        "unit": "",
        "name": "",
        "input": "",
        "accuracy": {
            "qty": None,
            "unit": None,
            "name": None,
        }
    }
    
    tokens = []
    name_parts = []
    name_accuracies = []
    
    for line in lines:
        if line in ('', '\n'):
            continue
            
        if line.startswith('#'):
            continue
            
        columns = line.strip().split('\t')
        if len(columns) >= 5:
            token = columns[0]
            tag_with_prob = columns[-1]
            tag, prob = tag_with_prob.split('/')
            accuracy = round(float(prob), 3)
            tokens.append(token)
            
            if tag.startswith('B-QTY'):
                ingredient["qty"] = token
                ingredient["accuracy"]["qty"] = accuracy
            elif tag.startswith('B-UNIT'):
                ingredient["unit"] = token
                ingredient["accuracy"]["unit"] = accuracy
            elif tag.startswith('B-NAME') or tag.startswith('I-NAME'):
                name_parts.append(token)
                name_accuracies.append(accuracy)
    
    # Join all name parts into a single string
    ingredient["name"] = ' '.join(name_parts)
    
    # Set name accuracy as average if we have name parts
    if name_accuracies:
        ingredient["accuracy"]["name"] = round(sum(name_accuracies) / len(name_accuracies), 3)
    
    # Set the input string
    ingredient["input"] = ' '.join(tokens)
    
    return ingredient

def export_data(lines):
    """ Parse "raw" ingredient lines into CRF-ready output """
    output = []
    for line in lines:
        line_clean = re.sub('<[^<]+?>', '', line)
        tokens = tokenizer.tokenize(line_clean)

        for i, token in enumerate(tokens):
            features = getFeatures(token, i + 1, tokens)
            output.append(joinLine([token] + features))
        output.append('')
        
    return '\n'.join(output)
