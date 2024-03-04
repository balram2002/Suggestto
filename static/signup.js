// const firebaseApp = firebase.initializeApp({
//   apiKey: "AIzaSyC07c0Du8ciKbd4R9_Nxa736gH-JJM13-8",
//   authDomain: "auth-mrs.firebaseapp.com",
//   projectId: "auth-mrs",
//   storageBucket: "auth-mrs.appspot.com",
//   messagingSenderId: "653550934375",
//   appId: "1:653550934375:web:ac142bd83ec3d0141977c2",
//   measurementId: "G-241T9GJTQZ"
// });
// const db = firebaseApp.firestore();
// const auth = firebaseApp.auth();

// const signUp = () => {
//   const email = document.getElementById("email").value;
//   const password = document.getElementById("password").value;
//   const success=document.getElementsByClassName("success");
//   firebase.auth().createUserWithEmailAndPassword(email, password)
//       .then((result) => {
//           $("#succ").css("display", "block");
//           window.alert("Registeration data Saves Successfully!");
//           console.log("Registeration data Saves Successfully!");
//       })
//       .catch((error) => {
//           console.log(error.code);
//           console.log(error.message);
//           // ..
//       });
// }


// const signIn = () => {
//   const email = document.getElementById("email").value;
//   const password = document.getElementById("password").value;
//   firebase.auth().signInWithEmailAndPassword(email, password)
//       .then((result) => {
//           // Signed in
//           window.location.href = "/home";
//           window.alert("Signed In Successfully!");
//           // ...
//       })
//       .catch((error) => {
//           $("#succe").css("display", "block");
//           console.log(error.code);
//           console.log(error.message);
//       });
// }

$("#iconlogin").click(function(){
    window.location.href = "/home";
  });

  $("#iconregister").click(function(){
    window.location.href = "/home";
  });  

  $("#logo").click(function(){
    window.alert("Login to go Home Page");
  }); 
  
  $("#home").click(function(){
    window.alert("Login to go Home Page");
  }); 

  $("#about").click(function(){
    window.alert("Login to go About Page");
  }); 

  $("#logoo").click(function(){
    window.alert("Login to go Home Page");
  }); 

  $("#homee").click(function(){
    window.alert("Login to go Home Page");
  }); 

  $("#aboutt").click(function(){
    window.alert("Login to go About Page");
  }); 

  $("#explore").click(function(){
    window.alert("Login to go Explore Page");
  }); 

  $("#exploree").click(function(){
    window.alert("Login to go Explore Page");
  }); 