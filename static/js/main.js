const productListBtn = document.getElementById('productListBtn')
const menuList = document.getElementById('menulist')
const upArrow = document.getElementById('upArrow')
const downArrow = document.getElementById('downArrow')

productListBtn.addEventListener('click', () => {
    if (menuList.style.display == 'none') {
        menuList.style.display = 'block'
        downArrow.style.display='none'
        upArrow.style.display='block'
    }
    else {
        menuList.style.display = 'none'
        downArrow.style.display='block'
        upArrow.style.display='none'
    }
})





// ===============product menu======




