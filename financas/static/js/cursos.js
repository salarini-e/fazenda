let filtros=[]
let curso=[]
function filtro(event){
    if(event.checked){
        filtros.push(event.value)
    }else{
        for(i=0; i<filtros.length; i++){
            if(filtros[i]==event.value){
                filtros.splice(i, 1)
            }
        }
    }
    
    console.log(filtros);
}

// function clickCandidato(e){    
//     options=document.getElementById('id_curso').children

//     for(i in options){
//         if(options[i].innerText==e.id){
//             curso={
//                 value: i,
//                 text: options[i].innerText
//             }
//             document.getElementById('id_curso').value=curso.value
//         }
//     }
// }


// function execAPI(form){
//     document.getElementById('loading').style.display='block'
//     url='/cursos/candidato/'
//     const data = new URLSearchParams();
//     for (const pair of new FormData(form)) {
//         data.append(pair[0], pair[1]);
//     }

//     fetch(url, {
//         method: 'post',
//         body: data,
//     })
//     .then(
//         data => {
//         console.log(data)
//         if(data.status==404){
//             console.log('Página não encontrada.');
//             document.getElementById('loading').style.display='none'
//             document.getElementById('tituloResponse').innerText='404 - Página não encontrada.'
//             document.getElementById('response').innerText='Erro para se comunicar com o servidor. O mesmo retornou com erro 404.'
//         }else if(data.status==200){
//             console.log(data)
//         }
//     }
//     );
// }

// function enviarFormulario(){
//     form=document.getElementById('form')
//     execAPI(form)
// }

window.onload=()=>{
    let btnfilter = document.querySelector(".btnfiltro")
    let div = document.querySelector(".filtragem")
    let favicon = document.querySelector(".fv")
    let spn = document.querySelector("#txt")
    btnfilter.addEventListener('click', ()=>{
        if(div.classList.contains("visually-hidden")){
            div.classList.remove("visually-hidden");
            favicon.classList.remove("fa-filter")
            favicon.classList.add("fa-filter-circle-xmark")
            spn.innerText = "Remover filtro"
        }
        else{
        filtros=[];
        console.log(filtros)
        
        div.classList.add("visually-hidden");
        favicon.classList.remove("fa-filter-circle-xmark")
        favicon.classList.add("fa-filter")
        spn.innerText = "Filtro"
        }
    })
}