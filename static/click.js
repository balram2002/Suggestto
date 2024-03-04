$("#balram").click(function () {
    window.alert("You will be redirected to Balram linkedIn Profile");
    window.open("https://www.linkedin.com/in/balram-dhakad-2a9110210?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app", '_blank');
});
$("#ayush").click(function () {
    window.alert("You will be redirected to Balram linkedIn Profile");
    window.open("https://www.linkedin.com/in/ayush-shukla-4064b324b?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app", '_blank');
});
$("#aditya").click(function () {
    window.alert("You will be redirected to Balram linkedIn Profile");
    window.open("https://www.linkedin.com/in/aaditya-choudhary-453a7a235?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app", '_blank');
});
$("#fb").click(function () {
    window.alert("You will be redirected to Balram linkedIn Profile");
    window.open("https://www.facebook.com/balram.dhakad.3551?mibextid=ZbWKwL", '_blank');
});
$("#wh").click(function () {
    window.alert("Contact NO. 9131116713 for whatsapp!");
});
$("#in").click(function () {
    window.alert("You will be redirected to Balram instagram Profile");
    window.open("https://instagram.com/balramdhakad12_?igshid=OGQ5ZDc2ODk2ZA==", '_blank');
});
$("#tw").click(function () {
    window.alert("You will be redirected to Balram twitter Profile");
    window.open("https://twitter.com/BalramD42013703?t=rRs-EpG6nl6V5N0Ys8jcAA&s=09", '_blank');
});
$("#footerlogo").click(function(){
    window.location.href = "/home";
  }); 

$("#cross").click(function(){
    $('#autocomplete').val('');
  }); 

$(".scroll").click(function(){
    $(window).scrollTop(0);
  }); 
$(".detailsarrow").click(function(){
    $(window).scrollTop(634);
  }); 
$(".castarrow").click(function(){
    $(window).scrollTop(1292.5);
  }); 
$(".rcmdarrow").click(function(){
    $(window).scrollTop(4080.5);
  }); 
$(".select-btn").click(function(){
    $(".searchcontent").css('display','block');
    $("#angle").css("transform","rotate(180deg)");
    $("#angle").css("top","-1px");
  });   
$("#closedr").click(function(){
    $(".searchcontent").css('display','none');
    $("#angle").css("transform","rotate(0deg)");
    $("#angle").css("top","3px");
  });
// $("body").click(function(){
//     $(".searchcontent").css('display','none');
//     $("#angle").css("transform","rotate(0deg)");
//     $("#angle").css("top","3px");
//   });  
$(".options li").click(function(){
  var title=$(this).text();
  $('#autocomplete').val(title);
  $(window).scrollTop(0);
  $(".searchcontent").css('display','none');
  $("#angle").css("transform","rotate(0deg)");
  $("#angle").css("top","3px");
}); 
$("#checkkk").click(function(){
  window.location.href = "/about";
});
$("#profileicon").click(function(){
  $(".profilemenu").css('display','block');
  $("#qwe").css('top','526.5px');
  $("#cross").css('top','524px');
});
$("#menucross").click(function(){
  $(".profilemenu").css('display','none');
  $("#qwe").css('top','410.5px');
  $("#cross").css('top','409px');
});
     
     
           
  
  