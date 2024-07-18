import traceback

try:
    main()
except Exception as e:
    print("An error occurred:", e)
    traceback.print_exc()
