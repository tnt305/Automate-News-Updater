#!/bin/bash

# Kiểm tra xem có đối số không
if [ -z "$1" ]; then
    echo "Usage: $0 <package_name>"
    exit 1
fi

PACKAGE=$1

# Hàm kiểm tra đầu vào chỉ được là "y" hoặc "n"
function ask_yes_no {
    local prompt="$1"
    local response

    while true; do
        read -p "$prompt (y/n): " response
        case "$response" in
            [Yy]) return 0 ;;
            [Nn]) return 1 ;;
            *) echo "❌ Invalid input! Please enter 'y' or 'n'." ;;
        esac
    done
}

# Hỏi người dùng package có dành cho môi trường production không
if ask_yes_no "Do you want to add $PACKAGE to production dependencies?"; then
    poetry add "$PACKAGE"
fi

# Hỏi tiếp package có dành cho dev không
if ask_yes_no "Do you also want to add $PACKAGE to dev dependencies?"; then
    poetry add --group dev "$PACKAGE"
fi

echo "✅ Installation complete!"
