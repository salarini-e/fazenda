    selecionado=[]
    opcao=''

    function acao(event){
      opcao=event.value
      console.log(opcao)
    }
    function selecionar(event){
      if(event.checked){
        nTemOValor=true
        for(i in selecionado){
          if(selecionado[i]==event.value){
            nTemOValor=false
          }
        }        
        if(nTemOValor){
          selecionado.push(event.value)
        }        
      }else{
        selecionado = selecionado.filter(data => data != event.value);
      }      
      console.log(selecionado)
    }

    function checkAll(){
      inputs=document.getElementsByTagName('input')
      for(i in inputs){        
        if(inputs[0].checked){        
          if(i!=0 && i!='length' && i!='item' && i!='namedItem'){
            
            inputs[i].checked=true

            var event = new Event('change');
            inputs[i].dispatchEvent(event);
            
          }
        }else{
          if(i!=0 && i!='length' && i!='item' && i!='namedItem'){
            
            inputs[i].checked=false

            selecionado=[]

          }
        }        
      }
    }