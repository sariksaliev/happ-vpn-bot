# from moviepy.editor import VideoFileClip
# import os
#
# # путь к папке media
# media_dir = r"C:\Users\salig\PycharmProjects\hap_vpn\happ_vpn_final\happ_vpn_final\media"
#
# # какие файлы нужно конвертировать
# files_to_convert = [
#     "инструкция на айфон.MOV",
#     "инструкция на телевизор.MOV",
# ]
#
# for filename in files_to_convert:
#     input_path = os.path.join(media_dir, filename)
#     output_path = os.path.splitext(input_path)[0] + ".mp4"
#
#     print(f"🎬 Конвертация {filename} → {os.path.basename(output_path)} ...")
#
#     try:
#         clip = VideoFileClip(input_path)
#         clip.write_videofile(
#             output_path,
#             codec="libx264",   # стандартный кодек H.264
#             audio_codec="aac", # стандартный аудио-кодек
#             threads=4,
#             preset="ultrafast" # быстро, без потери совместимости
#         )
#         clip.close()
#         print(f"✅ Готово: {output_path}")
#     except Exception as e:
#         print(f"⚠️ Ошибка при обработке {filename}: {e}")
