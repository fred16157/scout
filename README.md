# Scout

Scout은 Mask RCNN을 활용한 심해 영상 쓰레기 탐지 툴입니다.

이 툴의 가장 큰 기반이 되는 기술인 Mask RCNN은 Keras에서 사용할 수 있게 포팅한 [Mask_RCNN](https://github.com/matterport/Mask_RCNN) 라이브러리를 사용하여 구현했습니다. 이 라이브러리는 프로젝트 내 Mask_RCNN 경로에 포함되어 있습니다.

훈련에 사용된 데이터셋은 JAMSTEC의 [심해 쓰레기 이미지 데이터베이스](http://www.godac.jamstec.go.jp/catalog/dsdebris/metadataList?lang=en)에서 가져왔습니다.

Annotation이 포함된 데이터셋은 따로 [구글 드라이브 링크](https://drive.google.com/file/d/1SIxZcREb5TjFnmAuhIufvB5KQn7IGE1K/view?usp=sharing)로 올려드리겠습니다. 데이터셋을 보면 아시겠지만 모델 학습에 사용된 이미지가 적어서 정확도가 낮을수도 있으니 참고해주세요.

Annotation 작업은 [이 툴](https://www.robots.ox.ac.uk/~vgg/software/via/via.html)을 활용하였습니다.

현재 이 툴에서 탐지할 수 있는 쓰레기의 종류는 다음과 같습니다:

- 병
- 캔
- 타이어
- 로프

모델에 사용할 데이터셋과 모델이 훈련되는 boundingbox.py를 수정하여 탐지할 쓰레기의 종류를 변경할 수 있습니다.

훈련은 다음 명령어로 할 수 있습니다.
~~~
python boundingbox.py train --dataset=(데이터셋 경로) --weights=coco
~~~

## 실행하기

먼저 툴에 사용할 모델을 다운받습니다. 이 파일은 프로젝트 최상위 폴더에 넣어주세요.

[링크](https://drive.google.com/file/d/1h9oGMq-Vec8Mfr3rDx0QBYeaJSjb77t5/view?usp=sharing)

그 다음 requirements.txt 파일을 설치하여 필요한 라이브러리를 설치해줍니다.

~~~
pip install -r requirements.txt
~~~

만약 gpu를 사용한다면 명령어 하나를 더 입력해주세요.
~~~
pip install tensorflow-gpu==1.15.2
~~~

그리고 Mask_RCNN 라이브러리를 설치해야 합니다.

Mask_RCNN 폴더로 이동해서 설치해주세요.

~~~
cd Mask_RCNN
python setup.py install
~~~

그런 다음 최상위 폴더로 돌아와서 main.py를 실행해주면 툴이 작동합니다.

~~~
python main.py
~~~