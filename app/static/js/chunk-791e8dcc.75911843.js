(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-791e8dcc"],{"09d4":function(e,t,c){"use strict";c("7d9a")},"73cf":function(e,t,c){"use strict";c.r(t);var o=c("f2bf"),r=c("4841"),a=c.n(r),n=Object(o["withScopeId"])("data-v-2ebbdc3a");Object(o["pushScopeId"])("data-v-2ebbdc3a");var l={class:"container text-center"},i={class:"login"},s=Object(o["createVNode"])("img",{class:"logo",src:a.a},null,-1),d=Object(o["createVNode"])("h2",null,"Register",-1),u=Object(o["createVNode"])("div",{class:"full col-md-12"},[Object(o["createVNode"])("div",{id:"customBtn"},[Object(o["createVNode"])("span",{class:"buttonText"},"Register With Gmail")])],-1),m={key:0,class:"full col-md-12"},b=Object(o["createVNode"])("label",{for:"email"},"Gmail Address",-1),f=Object(o["createVNode"])("br",null,null,-1),g=Object(o["createVNode"])("label",{for:"fullname"},"Full Name",-1),p=Object(o["createVNode"])("br",null,null,-1),O=Object(o["createVNode"])("label",{for:"token"},"Token",-1),j=Object(o["createVNode"])("br",null,null,-1),h=Object(o["createVNode"])("button",{type:"submit"},"Register",-1);Object(o["popScopeId"])();var v=n((function(e,t,c,r,a,n){var v=Object(o["resolveComponent"])("Header");return Object(o["openBlock"])(),Object(o["createBlock"])(o["Fragment"],null,[Object(o["createVNode"])(v),Object(o["createVNode"])("div",l,[Object(o["createVNode"])("div",i,[Object(o["createVNode"])("form",{class:"login",onSubmit:t[4]||(t[4]=Object(o["withModifiers"])((function(){return n.register&&n.register.apply(n,arguments)}),["prevent"]))},[s,d,u,a.togleForm?(Object(o["openBlock"])(),Object(o["createBlock"])("div",m,[b,f,Object(o["withDirectives"])(Object(o["createVNode"])("input",{required:"","onUpdate:modelValue":t[1]||(t[1]=function(e){return a.gmail_address=e}),type:"text",id:"email",autocomplete:"off"},null,512),[[o["vModelText"],a.gmail_address]]),g,p,Object(o["withDirectives"])(Object(o["createVNode"])("input",{required:"","onUpdate:modelValue":t[2]||(t[2]=function(e){return a.fullname=e}),type:"text",id:"fullname",autocomplete:"off"},null,512),[[o["vModelText"],a.fullname]]),O,j,Object(o["withDirectives"])(Object(o["createVNode"])("input",{required:"","onUpdate:modelValue":t[3]||(t[3]=function(e){return a.token=e}),type:"text",id:"token",autocomplete:"off"},null,512),[[o["vModelText"],a.token]])])):Object(o["createCommentVNode"])("",!0),h],32)])])],64)})),N=c("5530"),V=c("e096"),k=c("5502"),w={name:"Register",components:{Header:V["a"]},data:function(){return{fullname:"",gmail_address:"",token:"",togleForm:!1}},methods:Object(N["a"])(Object(N["a"])({},Object(k["b"])({logoutUser:"auth/deleteAccessTokens",errorAlert:"errorAlert",successAlert:"successAlert"})),{},{getGmail:function(){var e=this,t=window.gapi,c="";t.load("auth2",(function(){c=t.auth2.init({client_id:"475271500037-5gg9viio8pftqjs1ra3aq9f3ss8f0nru.apps.googleusercontent.com",cookiepolicy:"single_host_origin"});var o=document.getElementById("customBtn");c.attachClickHandler(o,{},(function(t){e.togleForm=!0,e.gmail_address=t.getBasicProfile().getEmail(),e.fullname=t.getBasicProfile().getName()}),(function(t){e.errorAlert(JSON.stringify(t,void 0,2))}))}))},register:function(){var e=this;if(this.gmail_address.indexOf(" ")>0)this.errorAlert("username cant have space");else{var t={email:this.gmail_address,token:this.token,fullname:this.fullname};this.$store.dispatch("auth/register",t).then((function(t){e.successAlert(t.message),e.$router.push({name:"Login"})})).catch((function(t){e.errorAlert(t.message)}))}}}),mounted:function(){this.getGmail()},created:function(){this.logoutUser().then((function(e){})).catch((function(e){}))}};c("09d4");w.render=v,w.__scopeId="data-v-2ebbdc3a";t["default"]=w},"7d9a":function(e,t,c){}}]);
//# sourceMappingURL=chunk-791e8dcc.75911843.js.map