import json
from deepdiff import DeepDiff
from termcolor import colored

def highlight_diff(dict1, dict2):
    # Get the deep difference between the two structures
    diff = DeepDiff(dict1, dict2, verbose_level=2)

    def highlight_changes(diff):
        """Recursively highlight changes in the diff and print only differences"""
        output = []
        
        # Highlight changed values
        if "values_changed" in diff:
            for path, change in diff["values_changed"].items():
                old_value = change["old_value"]
                new_value = change["new_value"]
                output.append(colored(f"Changed: {path} | Old Value: {old_value} -> New Value: {new_value}", 'red'))

        # Highlight added items
        if "dictionary_item_added" in diff:
            for path, item in diff["dictionary_item_added"].items():
                output.append(colored(f"Added: {path} | New Item: {json.dumps(item)}", 'green'))

        # Highlight removed items
        if "dictionary_item_removed" in diff:
            for path, item in diff["dictionary_item_removed"].items():
                output.append(colored(f"Removed: {path} | Removed Item: {json.dumps(item)}", 'yellow'))

        return '\n'.join(output)

    # Print only the differences
    print(highlight_changes(diff))

