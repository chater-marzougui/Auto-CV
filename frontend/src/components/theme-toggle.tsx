import { Moon, Sun } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useTheme } from "@/components/theme-provider"

export function ThemeToggle() {
  const { theme, setTheme } = useTheme()

  const toggleTheme = () => {
    const next =
      theme === "light" ? "dark" : "light"
    setTheme(next)
  }

  const getIcon = () => {
    if (theme === "light") return <Sun className="h-6 w-6" />
    return <Moon className="h-6 w-6" />
  }

  const getColor = () => {
    if (theme === "dark") {
      return "text-gray-300 hover:text-gray-400"
    }
    return "text-yellow-500 hover:text-yellow-600"
  }

  const getTitle = () => {
    if (theme === "light") return "Switch to dark mode"
    return "Switch to light mode"
  }

  return (
    <Button
      variant="secondary"
      size="icon"
      onClick={toggleTheme}
      title={getTitle()}
      className={"h-8 w-8 " + getColor()}
      aria-label="Toggle theme"
    >
      {getIcon()}
      <span className="sr-only">Toggle theme</span>
    </Button>
  )
}
