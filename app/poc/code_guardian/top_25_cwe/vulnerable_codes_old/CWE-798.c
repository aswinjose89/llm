int VerifyAdmin(char *password) {
if (strcmp(password, "Mew!")) {
printf("Incorrect Password!\n");
return(0)
}
printf("Entering Diagnostic Mode...\n");
return(1);
}
