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
	multiline_output := formatted_multiline_output("test_multiline", `
	Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. 
	Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. 
	Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. 
	Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. 
	Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibus. Vivamus elementum semper nisi. 
	Aenean vulputate eleifend tellus. Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. 
	Aliquam lorem ante, dapibus in, viverra quis, feugiat a, tellus. Phasellus viverra nulla ut metus varius laoreet. 
	Quisque rutrum. Aenean imperdiet. Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi. Nam eget dui. 
	Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed ipsum. 
	Nam quam nunc, blandit vel, luctus pulvinar, hendrerit id, lorem. Maecenas nec odio et ante tincidunt tempus. 
	Donec vitae sapien ut libero venenatis faucibus. Nullam quis ante. Etiam sit amet orci eget eros faucibus tincidunt. 
	Duis leo. Sed fringilla mauris sit amet nibh. Donec sodales sagittis magna. Sed consequat, leo eget bibendum sodales, augue velit cursus nunc,
	`)
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
