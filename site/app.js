"use strict";
const $=id=>document.getElementById(id);
const siteState={config:null,entries:[],active:null,mode:"learner",details:new Map(),photoIndex:{}};
const hub="https://crking92.github.io/Hays-County-Botany/";
function setText(node,text){node.textContent=String(text??"");return node}
function el(tag,text,cls){const n=document.createElement(tag);if(text!==undefined)setText(n,text);if(cls)n.className=cls;return n}
function clear(node){node.replaceChildren()}
function statusMessage(title,body){const d=$("detail");clear(d);d.append(el("h3",title),el("p",body))}
function renderList(){
 const result=$("results");clear(result);
 const q=$("search").value.trim().toLocaleLowerCase();
 const list=siteState.entries.filter(x=>(String(x.scientific_name||"")+" "+String(x.common_name||"")).toLocaleLowerCase().includes(q));
 if(!siteState.entries.length){result.append(el("p","No species imported yet. The existing main Hays Botany learner still contains the authoritative cards.","muted"));return}
 if(!list.length){result.append(el("p","No matching plants in this collection.","muted"));return}
 for(const s of list){
   const b=el("button");b.type="button";
   const photos=siteState.photoIndex[s.id];
   if(photos?.count&&photos.first_src){
     const thumb=document.createElement("img");thumb.className="result-thumb";thumb.src=photos.first_src;thumb.loading="lazy";thumb.alt="";thumb.onerror=()=>thumb.remove();b.append(thumb);
   }
   b.append(el("strong",s.common_name||s.scientific_name),el("em",s.scientific_name));
   if(photos?.count)b.append(el("small",photos.count+" verified photo"+(photos.count===1?"":"s"),"photo-count"));
   if(s.id===siteState.active)b.setAttribute("aria-current","true");
   b.addEventListener("click",()=>select(s.id,true));result.append(b);
 }
}
async function select(id,push){
 const r=siteState.entries.find(x=>x.id===id);
 if(!r){statusMessage("Plant not available","That species has not been imported or verified in this family collection.");return}
 siteState.active=id;renderList();
 if(push){const url=new URL(location.href);url.searchParams.set("species",id);history.pushState({species:id},"",url)}
 const d=$("detail");clear(d);d.append(el("p",r.family+" · "+r.genus,"sectionnum"),el("h3",r.common_name||r.scientific_name),el("p",r.scientific_name,"latin"));
 try{
   if(!siteState.details.has(id)){
     const resp=await fetch("data/species/"+encodeURIComponent(id)+".json");
     if(!resp.ok)throw Error("Verified teaching summary is not available yet");
     siteState.details.set(id,await resp.json());
   }
   if(siteState.active!==id)return;
   const card=siteState.details.get(id);
   const released=Array.isArray(card.verified_photos)?card.verified_photos.length:0;
   d.append(el("p",released?`${released} individually credited Creative Commons photograph${released===1?"":"s"} available for this species. More anatomy views may still be needed.`:"No public-cleared photographs for this species yet. Field-ID text is available; archived source images remain under review.","muted"));
   if(card.look_here_first){
     d.append(el("h3","LOOK HERE FIRST"));
     d.append(el("p",card.look_here_first));
   }
   if(siteState.mode==="learner" && Array.isArray(card.key_traits)&&card.key_traits.length){
     d.append(el("h3","Anatomy and field recognition"));
     const list=el("ul");
     for(const trait of card.key_traits.slice(0,10)){
       const li=el("li");li.append(el("strong",trait.label+": "),document.createTextNode(trait.text));list.append(li);
     }
     d.append(list);
   }
   if(card.lookalikes){
     d.append(el("h3","Look-alikes"));
     if(card.lookalikes.names?.length)d.append(el("p","Compare with: "+card.lookalikes.names.join(", ")));
     if(card.lookalikes.differences)d.append(el("p",card.lookalikes.differences));
   }
   if(Array.isArray(card.verified_photos)&&card.verified_photos.length){
     const heading=el("h3","Real species photographs");d.append(heading);
     d.append(el("p","Scroll sideways to compare the photographed structures. Image rights vary by photograph; review each caption. Anatomy arrows have not yet been individually certified.","muted"));
     const strip=el("div",undefined,"gallery-strip");
     for(const photo of card.verified_photos){
       const fig=el("figure",undefined,"gallery-photo");
       const link=document.createElement("a");link.href=photo.src;link.target="_blank";link.rel="noopener noreferrer";link.setAttribute("aria-label","Open original-size preview of "+(photo.role||card.scientific_name));
       const image=document.createElement("img");image.src=photo.src;image.loading="lazy";image.alt=card.scientific_name+": "+(photo.role||"verified species photograph");
       link.append(image);fig.append(link);
       const cap=el("figcaption");cap.append(el("strong",photo.role||"Species photograph"),el("small","Photo: "+photo.creator+" · "+photo.license+". "+(photo.modified||"Source credited.")));
       if(photo.noncommercial_only)cap.append(el("small","NONCOMMERCIAL-ONLY reuse. No commercial use or redistribution outside license terms.","photo-nc"));
       if(photo.private_rights_review_only)cap.append(el("small",photo.rights_note||"Private review: public license verification still required.","photo-review"));
       const sources=el("div",undefined,"source-links");
       for(const [label,url] of [[photo.source_page_is_exact===false?"Related iNaturalist reference (exact photo page pending)":"Photo source",photo.source_page],["License",photo.license_url]]){
         if(!url||!url.startsWith("https://"))continue;
         const a=el("a",label);a.href=url;a.target="_blank";a.rel="noopener noreferrer";sources.append(a);
       }
       cap.append(sources);fig.append(cap);strip.append(fig);
     }
     d.append(strip);
   }else d.append(el("p","Photographs for this species are held for source-rights or visual review. Its text lesson is available; see the current main learner for any existing images.","muted"));

 }catch(error){
   if(siteState.active===id)d.append(el("p","Teaching summary pending: "+error.message,"muted"));
 }
}
async function renderFamilyLesson(){
 const summary=$("family-lesson-summary"),diagnostics=$("family-diagnostics"),steps=$("family-lesson-steps");
 if(!summary||!diagnostics||!steps)return;
 try{
   const response=await fetch("data/family-lesson.json",{cache:"no-store"});
   if(!response.ok)throw Error("Family lesson JSON is unavailable");
   const lesson=await response.json();
   if(lesson.family!=="Fabaceae"||!Array.isArray(lesson.steps))throw Error("Family lesson data not recognized");
   summary.textContent=lesson.first_look;
   const terms=[["Leaves",lesson.diagnostics.leaves],["Flowers",lesson.diagnostics.flowers],["Fruit",lesson.diagnostics.fruit],["Field tip",lesson.diagnostics.field_tip]];
   const list=el("div",undefined,"family-diagnostic-grid");
   for(const [title,value] of terms){if(!value)continue;const item=el("div",undefined,"family-diagnostic");item.append(el("strong",title),el("p",value));list.append(item)}
   diagnostics.replaceChildren(list);
   const heading=el("h3","Learn by real photo examples");
   steps.replaceChildren(heading);
   for(const step of lesson.steps){
     const card=el("article",undefined,"family-step");
     const caption=el("div",undefined,"family-step-body");
     caption.append(el("span",String(step.sequence).padStart(2,"0")+" · FAMILY STRUCTURE","sectionnum"),el("h4",step.title));
     caption.append(el("p",step.look_for));
     caption.append(el("p",step.why_it_matters,"muted"));
     const view=el("button","Open this species lesson →","family-species-link");view.type="button";
     view.addEventListener("click",()=>{select(step.species_id,true);$("detail").scrollIntoView({behavior:"smooth",block:"start"})});
     caption.append(view);
     const media=el("div",undefined,"family-step-media");
     const species=siteState.entries.find(x=>x.id===step.species_id);
     if(species){
       try{
         const resp=await fetch("data/species/"+encodeURIComponent(step.species_id)+".json");
         if(resp.ok){
           const data=await resp.json(),images=data.verified_photos||[];
           const photo=images[step.image_index]||images[0];
           if(photo?.src?.startsWith("media/"+step.species_id+"/")&&!photo.private_rights_review_only&&!photo.noncommercial_only){
             const img=document.createElement("img");img.src=photo.src;img.loading="lazy";img.alt=(species.common_name||species.scientific_name)+": "+(photo.role||"approved family reference");
             media.append(img);
             const attribution=el("p","Photo: "+photo.creator+" · "+photo.license,"family-photo-credit");
             media.append(attribution);
           }else media.append(el("p","A public-cleared photograph is not available for this teaching example yet.","muted"));
         }else media.append(el("p","Photographic teaching example is not available yet.","muted"));
       }catch(err){media.append(el("p","Photo reference unavailable.","muted"))}
     }else media.append(el("p","Historic family teaching example needs a current species card.","muted"));
     card.append(media,caption);steps.append(card);
   }
 }catch(error){summary.textContent="Family teaching module is not available yet: "+error.message;diagnostics.replaceChildren();steps.replaceChildren()}
}

function setMode(mode){
 siteState.mode=mode;
 for(const b of document.querySelectorAll("[data-mode]"))b.setAttribute("aria-pressed",String(b.dataset.mode===mode));
 $("nav-learner").setAttribute("aria-current",mode==="learner"?"page":"false");
 $("nav-field").setAttribute("aria-current",mode==="field"?"page":"false");
 if(siteState.active)select(siteState.active,false);
 else statusMessage(mode==="learner"?"Choose a species to begin":"Choose a field ID lesson","Choose a species from the collection, or explore the full photo-backed Fabaceae family lesson above to begin, with approved photographs where available.");
}
async function boot(){
 try{
   const [confResp,indexResp]=await Promise.all([fetch("data/collection-meta.json"),fetch("data/collection-index.json")]);
   if(!confResp.ok||!indexResp.ok)throw Error("collection metadata missing");
   siteState.config=await confResp.json();const doc=await indexResp.json();
   try{const p=await fetch("data/gallery-index.json");if(p.ok){const list=await p.json();if(list.schema_version===1&&list.status==="ONLY_EXISTING_PUBLIC_RIGHTS_CLEARED_SITE_IMAGES"){siteState.photoIndex=list.entries;if($("photo-summary"))$("photo-summary").textContent=list.photo_count+" verified photographs across "+list.photo_species+" species";}}}catch(e){console.warn("Gallery thumbnail summary unavailable; full card galleries still load",e)}
   if(!Array.isArray(doc.entries))throw Error("invalid collection index");
   siteState.entries=doc.entries;
   const familyToggle=$("family-lesson-toggle"),familyContent=$("family-lesson-content");
   familyToggle?.addEventListener("click",()=>{
     const show=familyToggle.getAttribute("aria-expanded")!=="true";
     familyToggle.setAttribute("aria-expanded",String(show));
     familyContent.hidden=!show;
     familyToggle.textContent=show?"Hide family lesson":"Show family lesson";
   });
   renderFamilyLesson();
   const label=siteState.config.repository_full_name.split("/")[1].replace("Hays-Botany-","").replaceAll("-"," ");
   $("collection-title").textContent=label+" Visual Learner";
   $("family-count").textContent=siteState.config.family_assignments.length;
   $("species-count").textContent=siteState.entries.length;
   for(const b of document.querySelectorAll("[data-mode]"))b.addEventListener("click",()=>setMode(b.dataset.mode));
   $("nav-learner").addEventListener("click",()=>setMode("learner"));
   $("nav-field").addEventListener("click",()=>setMode("field"));
   $("search").addEventListener("input",renderList);
   window.addEventListener("popstate",()=>{const id=new URLSearchParams(location.search).get("species");if(id)select(id,false);else{siteState.active=null;renderList();statusMessage("Choose a species to begin","Select a verified plant from the collection.")}});
   renderList();
   const wanted=new URLSearchParams(location.search).get("species");
   if(wanted)select(wanted,false);else setMode("learner");
 }catch(e){statusMessage("Preview could not load",e.message)}
}
boot();
