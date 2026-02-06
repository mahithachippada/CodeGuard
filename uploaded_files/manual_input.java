var user = "admin";                
var password = "admin123";          

function login(u, p) {              
    if (u == "admin") {
        eval("console.log('Hi')");  
    }

    console.log("Debug login");     
}

login(user, password);