# easy to use torckvision transforms (helper module)

# easy_transforms.py
import torchvision.transforms as T

class EasyTransforms:
    """
    간단하게 이미지 전처리를 구성할 수 있는 헬퍼 클래스.
    예: EasyTransforms(mode='train').get()
    """
    def __init__(self, mode='train', image_size=224, normalize=True):
        self.mode = mode
        self.image_size = image_size
        self.normalize = normalize

    def get(self):
        """
        torchvision.transforms.Compose 형태로 반환
        """
        transform_list = []

        # Resize + ToTensor
        transform_list.append(T.Resize((self.image_size, self.image_size)))
        transform_list.append(T.ToTensor())

        # Normalize
        if self.normalize:
            transform_list.append(
                T.Normalize(mean=[0.485, 0.456, 0.406],
                            std=[0.229, 0.224, 0.225])
            )

        # Train일 경우 data augmentation 추가
        if self.mode == 'train':
            transform_list.insert(0, T.RandomHorizontalFlip())
            transform_list.insert(0, T.RandomRotation(10))
            transform_list.insert(0, T.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2))

        return T.Compose(transform_list)

    def summary(self):
        """
        현재 구성된 transform을 보기 쉽게 출력
        """
        t = self.get()
        print("=== EasyTransforms 구성 ===")
        for i, tr in enumerate(t.transforms):
            print(f"{i+1}. {tr}")
        print("===========================")


# 예시 사용법
if __name__ == "__main__":
    train_t = EasyTransforms(mode='train', image_size=224).get()
    test_t = EasyTransforms(mode='test', image_size=224).get()

    # 요약 보기
    EasyTransforms(mode='train').summary()
