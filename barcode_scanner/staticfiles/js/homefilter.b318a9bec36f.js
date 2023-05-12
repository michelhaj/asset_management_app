let grid = document.querySelector(".products");
let filterInput = document.getElementById("filterInput");


filterInput.addEventListener('keyup', filterProducts);

// callback function 
function filterProducts(){
    let filterValue = filterInput.value.toUpperCase();
    let item = grid.querySelectorAll('.cardd')
    // console.log(filterValue);

    for (let i = 0; i < item.length; i++){
        let span = item[i].querySelector('.title');
        let modelMake=item[i].querySelector('.modelmake');
        let serviceTag=item[i].querySelector('.servicetag');
        let user=item[i].querySelector('.user');
        let comp=item[i].querySelector('.computername1');

        if((span.innerHTML.toUpperCase().indexOf(filterValue) > -1)|| (modelMake.innerHTML.toUpperCase().indexOf(filterValue) > -1)
        ||(serviceTag.innerHTML.toUpperCase().indexOf(filterValue) > -1)||(user.innerHTML.toUpperCase().indexOf(filterValue) > -1)||(comp.innerHTML.toUpperCase().indexOf(filterValue) > -1)) {
            item[i].style.display = "initial";
        }else{
            item[i].style.display = "none";
        }

    }
}

