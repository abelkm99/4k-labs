(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-e82ea640"],{"800a":function(e,t,n){},a55b:function(e,t,n){"use strict";n.r(t);var o=n("f2bf"),c=n("4841"),s=n.n(c),i=Object(o["withScopeId"])("data-v-b512d76c");Object(o["pushScopeId"])("data-v-b512d76c");var r=Object(o["createVNode"])("div",{class:"container text-center"},[Object(o["createVNode"])("div",{class:"login"},[Object(o["createVNode"])("form",{class:"login",onsubmit:"return false"},[Object(o["createVNode"])("img",{class:"logo",src:s.a}),Object(o["createVNode"])("h2",null,"Login"),Object(o["createVNode"])("div",{id:"google-signin-button"})])])],-1),a=Object(o["createVNode"])("div",{class:"footer text-center"},[Object(o["createVNode"])("p",null,"4K Labs - 2021")],-1);Object(o["popScopeId"])();var u=i((function(e,t,n,c,s,i){var u=Object(o["resolveComponent"])("Header");return Object(o["openBlock"])(),Object(o["createBlock"])(o["Fragment"],null,[Object(o["createVNode"])(u),r,a],64)})),d=n("5530"),l=n("e096"),b=n("5502"),h={name:"Login",components:{Header:l["a"]},data:function(){return{password:"",username:""}},computed:Object(d["a"])({},Object(b["c"])({isAuthenticated:["auth/isAuthenticated"],isSuperAdmin:["user/isSuperAdmin"]})),methods:Object(d["a"])(Object(d["a"])({},Object(b["b"])({errorAlert:"errorAlert",successAlert:"successAlert",loginUser:"auth/loginUser",logoutUser:"auth/logoutUser2"})),{},{onSignIn:function(e){var t=this,n=e.getAuthResponse().id_token;this.loginUser(n).then((function(e){t.successAlert("login successfull"),t.$router.push({name:"Divisions"})})).catch((function(e){t.errorAlert(e.message)}))},onFailure:function(e){this.errorAlert(e)}}),mounted:function(){if(this.isSuperAdmin)this.logoutUser();else if(this.isAuthenticated)this.$router.push({name:"Divisions"});else{var e=window.gapi;e.signin2.render("google-signin-button",{onsuccess:this.onSignIn,onfailure:this.onFailure,width:240,height:50,longtitle:!0,theme:"white"})}}};n("a67c");h.render=u,h.__scopeId="data-v-b512d76c";t["default"]=h},a67c:function(e,t,n){"use strict";n("800a")}}]);
//# sourceMappingURL=chunk-e82ea640.cb07de9a.js.map