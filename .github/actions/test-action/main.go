package main

import (
	"fmt"
	"os"

	"github.com/google/uuid"
)

func check(e error) {
	if e != nil {
		panic(e)
	}
}

func formatted_output(name, content string) (output string) {
	return fmt.Sprintf("%s=%s\n", name, content)
}

func formatted_multiline_output(name, content string) (output string) {
	sep := uuid.New()
	output = fmt.Sprintf("%s<<%s\n", name, sep)
	output = output + content + "\n"
	output = output + sep.String() + "\n"
	return output
}

func main() {
	output_path := os.Getenv("GITHUB_OUTPUT")
	output_1 := formatted_output("test", "ABC")
	output_2 := formatted_output("test2", "ABC2")
	multiline_output := formatted_multiline_output("test_multiline", "CDE")
	file, err := os.OpenFile(output_path, os.O_APPEND|os.O_WRONLY, os.ModeAppend)
	check(err)
	defer file.Close()
	_, err = file.WriteString(output_1)
	check(err)
	_, err = file.WriteString(output_2)
	check(err)
	_, err = file.WriteString(multiline_output)
	check(err)
}
