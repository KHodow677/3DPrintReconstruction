from ultralytics import YOLO
import cv2
import argparse
import supervision as sv

# Test Change

def parse_arguments() -> argparse.Namespace:    #Define Webcam Resolution
    parser = argparse.ArgumentParser(description="yolov8")
    parser.add_argument(
        "--webcam-resolution",
        default=[1280,720],
        nargs=2,
        type=int
    )
    args = parser.parse_args()
    return args

def main():
    args = parse_arguments()
    frame_width, frame_height = args.webcam_resolution

    cap = cv2.VideoCapture(0)   #Capture Video From Camera
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)

    model = YOLO("Documents/yolov8/best.pt")    #Run YOLO on model

    box_annotator = sv.BoxAnnotator(
        thickness=2,
        text_thickness=2,
        text_scale=1
    ) 
    
    while True:
        ret, frame = cap.read()

        result = model(frame)[0]
        detections = sv.Detections.from_ultralytics(result)     #Runs Dection
        labels = [
            f"{model.model.names[class_id]} {confidence:0.2f}"
            for _, confidence, class_id, _
            in detections
        ]   #Label Failures and Confidence Rate

        frame = box_annotator.annotate(
            scene=frame,
            detections=detections,
            labels=labels)

        cv2.imshow("yolov8", frame)     #Outputs Frame

        if (cv2.waitKey(0) == 30):      #Break Using Esc
            break
        

if __name__ == "__main__":
    main()