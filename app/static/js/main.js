const toggle=document.querySelector('[data-menu-toggle]');
const menu=document.querySelector('[data-menu]');
if(toggle&&menu)toggle.addEventListener('click',()=>menu.classList.toggle('open'));
document.querySelectorAll('.flash').forEach((el)=>setTimeout(()=>{el.style.opacity='0';setTimeout(()=>el.remove(),300)},4500));
document.querySelectorAll('.newsletter').forEach(form=>form.addEventListener('submit',event=>{event.preventDefault();form.innerHTML='<span>Bem-vindo ao nosso clima.</span>'}));

document.querySelectorAll('[data-variant-configurator]').forEach(form=>{
  const variants=[...form.querySelectorAll('[data-variant-option]')];
  const quantity=form.elements.quantity;
  const update=()=>{
    const color=form.elements.color_choice.value;
    const size=form.elements.size_choice.value;
    const variant=variants.find(item=>item.dataset.color===color&&item.dataset.size===size);
    const stock=Number(variant?.dataset.stock||0);
    form.querySelector('[data-variant-id]').value=variant?.dataset.id||'';
    const selectedColor=form.querySelector('[name="color_choice"]:checked');
    form.querySelector('[data-color-name]').textContent=selectedColor.dataset.label;
    form.querySelector('[data-size-name]').textContent=form.querySelector('[name="size_choice"]:checked').dataset.label;
    form.querySelector('[data-selection-summary]').textContent=`${selectedColor.dataset.label} · ${form.querySelector('[name="size_choice"]:checked').dataset.label}`;
    form.querySelector('[data-stock-status]').textContent=stock===0?'Combinação indisponível':stock<=5?`Restam apenas ${stock} unidades`:`Em estoque — ${stock} unidades`;
    quantity.max=Math.max(1,stock);
    form.querySelector('button[type="submit"]').disabled=stock===0;
    if(selectedColor.dataset.image)document.querySelectorAll('[data-product-image]').forEach(image=>image.src=selectedColor.dataset.image);
  };
  form.addEventListener('change',update);
  update();
});

document.querySelectorAll('[data-size-guide]').forEach(button=>{
  const dialog=document.querySelector('[data-size-dialog]');
  button.addEventListener('click',()=>dialog?.showModal());
  dialog?.querySelector('[data-size-close]')?.addEventListener('click',()=>dialog.close());
});

