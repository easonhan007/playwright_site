package main

import (
	"bufio"
	"bytes"
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
	"strings"
	"time"
)

func printHelp() {
	fmt.Println("newblog - Create a new blog post directory with frontmatter")
	fmt.Println()
	fmt.Println("USAGE:")
	fmt.Println("    newblog <directory-name>")
	fmt.Println("    newblog -h|--help")
	fmt.Println()
	fmt.Println("DESCRIPTION:")
	fmt.Println("    Creates a new directory in content/blog/ with an index.md file.")
	fmt.Println("    The frontmatter is copied from the latest index.md file,")
	fmt.Println("    with the date updated to the current day.")
	fmt.Println()
	fmt.Println("EXAMPLE:")
	fmt.Println("    newblog my-new-post")
}

func main() {
	if len(os.Args) < 2 {
		printHelp()
		os.Exit(1)
	}

	if os.Args[1] == "-h" || os.Args[1] == "--help" {
		printHelp()
		os.Exit(0)
	}

	dirName := strings.TrimSpace(os.Args[1])
	blogDir := filepath.Join("content", "blog", dirName)
	targetFile := filepath.Join(blogDir, "index.md")

	// 检查目录是否已存在
	if _, err := os.Stat(blogDir); err == nil {
		fmt.Printf("Error: directory '%s' already exists\n", dirName)
		os.Exit(1)
	}

	// 创建新目录
	if err := os.MkdirAll(blogDir, 0755); err != nil {
		fmt.Printf("Error creating directory: %v\n", err)
		os.Exit(1)
	}

	// 查找最新的 index.md
	latestIndex, err := findLatestIndexMD("content/blog")
	if err != nil {
		fmt.Printf("Error finding latest index.md: %v\n", err)
		os.Exit(1)
	}

	// 提取 frontmatter
	frontmatter, err := extractFrontmatter(latestIndex)
	if err != nil {
		fmt.Printf("Error extracting frontmatter: %v\n", err)
		os.Exit(1)
	}

	// 更新 date 为当前日期
	updatedFrontmatter := updateDate(frontmatter)

	// 写入新文件
	if err := os.WriteFile(targetFile, []byte(updatedFrontmatter), 0644); err != nil {
		fmt.Printf("Error writing file: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("Created: %s/index.md\n", blogDir)
}

func findLatestIndexMD(baseDir string) (string, error) {
	var latestPath string
	var latestTime time.Time

	err := filepath.WalkDir(baseDir, func(path string, d fs.DirEntry, err error) error {
		if err != nil {
			return err
		}
		if d.IsDir() || d.Name() != "index.md" {
			return nil
		}

		info, err := d.Info()
		if err != nil {
			return err
		}

		if info.ModTime().After(latestTime) {
			latestTime = info.ModTime()
			latestPath = path
		}
		return nil
	})

	if err != nil {
		return "", err
	}

	if latestPath == "" {
		return "", fmt.Errorf("no index.md found")
	}

	return latestPath, nil
}

func extractFrontmatter(filePath string) (string, error) {
	file, err := os.Open(filePath)
	if err != nil {
		return "", err
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	var frontmatter strings.Builder
	inFrontmatter := false

	for scanner.Scan() {
		line := scanner.Text()
		if line == "+++" {
			if !inFrontmatter {
				inFrontmatter = true
				frontmatter.WriteString(line + "\n")
			} else {
				frontmatter.WriteString(line + "\n")
				break
			}
		} else if inFrontmatter {
			frontmatter.WriteString(line + "\n")
		}
	}

	return frontmatter.String(), nil
}

func updateDate(frontmatter string) string {
	now := time.Now()
	currentDate := now.Format("2006-01-02")

	// 替换 date 行
	var buf bytes.Buffer
	scanner := bufio.NewScanner(strings.NewReader(frontmatter))

	for scanner.Scan() {
		line := scanner.Text()
		if strings.HasPrefix(line, "date = ") {
			buf.WriteString(fmt.Sprintf("date = %s\n", currentDate))
		} else {
			buf.WriteString(line + "\n")
		}
	}

	return buf.String()
}
