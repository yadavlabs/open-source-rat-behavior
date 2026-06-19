/*
  This is an interface to contain values relevant to the selection menus.
    There is a view value that will be displayed in the selection menu for the
    user to see, and there is a value that is actually used for the function
    to be processed.
*/

export interface DropDownInfo {
    value: string;
    viewValue: string;
}
