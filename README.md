This is a responsive Django web app that I created with the help of my friend Zaid Karadsheh, its goal is to make the life of the IT department at any company easier by allowing them to manage their assets on any platform available. This web app utilizes a third-party Java script package to scan for barcodes (Asset Tag) and auto-fill that scanned barcode into a form where the user can easily fill in other relevant fields and then save update or even delete the item. there are four items that can be managed a Computer/Laptop, a Docking station, a Monitor, and a printer.

![main img](https://github.com/michelhaj/asset_management_app/assets/36920883/4701d643-963e-42cd-be5e-88e7710b28a2)


Features Breakdown
01.Home Page

![Inventory management system_desktop](https://github.com/michelhaj/asset_management_app/assets/36920883/fc6741b9-9bd0-43c7-8c32-08f477551d73)

This page contains a side menu and a main grid containing computers that can be filtered by typing in the filter box. Each computer has a view button and a list of printers, docking stations, and monitors connected to it.

 02.View/Update/Delete Page
 
![https __michelhajdemo pythonanywhere com_view page](https://github.com/michelhaj/asset_management_app/assets/36920883/fe3794da-39cb-4663-886f-b04301cbc543)

On this page, as the name reveals; the user can view, update, or delete an item it can be a computer/laptop, monitor, docking station, or printer.

03. Item's List page
   
![https __michelhajdemo pythonanywhere com_list page](https://github.com/michelhaj/asset_management_app/assets/36920883/77f920f4-3670-42a6-9ff5-2bfb65c46474)

This is where the independent assets information can be filtered, viewed, and imported as PDF, Excel, CSV, and copied to a clipboard, you can adjust and control what columns (attributes) you want to be visible.

04. Add Assets Page

![Inventory management system_scan page](https://github.com/michelhaj/asset_management_app/assets/36920883/d9269838-10ad-4143-91bc-3b3a86fd6fa1)

Here you can either choose to manually add the assets or scan the barcode (Asset Tag) to get an empty form in case of add manually was chosen or to get a prefilled Asset Tag in case of a successful scan of the Barcode. if the item is already in the database and you scan the barcode a popup will show and state that the asset being scanned is already in the database and you will be redirected to a form containing the asset information.


finally, there is an animated popup that shows whenever an action is successful.

![notification full size](https://github.com/michelhaj/asset_management_app/assets/36920883/c47ffe97-c0c5-485a-8a47-b1a4ccd2e480)
    usernamedemo
    password:demo2024
